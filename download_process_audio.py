#!/usr/bin/env python3
import ssl
import os
import sys
import time
import shutil
import yt_dlp
import numpy as np
import soundfile as sf
import librosa
import noisereduce as nr
from tqdm import tqdm
from pydub import AudioSegment

# Configure SSL context to handle potential certificate issues
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Function to reduce noise from audio file
def reduce_noise(audio_file, noise_duration=2.0, chunk_duration=30):
    """
    Reduce noise from an audio file.
    
    Args:
        audio_file (str): Path to input audio file
        noise_duration (float): Duration for noise sampling (seconds)
        chunk_duration (float): Duration for chunk processing (seconds)
        
    Returns:
        str: Path to the output file
    """
    try:
        # Determine file size
        file_size = os.path.getsize(audio_file) / (1024 * 1024)  # Convert to MB
        print(f"Processing file: {audio_file}")
        print(f"File size: {file_size:.2f} MB")
        
        # For large files (>100MB), use mono loading
        mono = file_size > 100
        print(f"Loading audio {'(mono)' if mono else '(stereo)'}")
        
        # Load audio file with librosa
        start_time = time.time()
        try:
            audio_data, sr = librosa.load(audio_file, sr=None, mono=mono)
        except Exception:
            # If librosa fails, try with soundfile
            print("Librosa loading failed, trying with soundfile...")
            audio_data, sr = sf.read(audio_file)
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)  # Convert to mono
        
        load_time = time.time() - start_time
        print(f"Audio loaded in {load_time:.2f} seconds, sample rate: {sr} Hz")
        
        # Extract noise sample from the beginning
        print(f"Extracting noise sample (first {noise_duration} seconds)")
        noise_sample = audio_data[:int(noise_duration * sr)]
        
        print("Applying noise reduction...")
        
        # For large files, use chunk processing
        chunk_size = int(chunk_duration * sr)
        total_chunks = int(np.ceil(len(audio_data) / chunk_size))
        
        start_time = time.time()
        
        if total_chunks > 1:
            # Chunk processing
            reduced_noise = np.zeros_like(audio_data)
            
            with tqdm(total=total_chunks, desc="Processing progress") as pbar:
                for i in range(total_chunks):
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, len(audio_data))
                    chunk = audio_data[start_idx:end_idx]
                    
                    # Apply noise reduction to each chunk
                    reduced_chunk = nr.reduce_noise(y=chunk, y_noise=noise_sample, sr=sr)
                    
                    # Store the processed chunk
                    reduced_noise[start_idx:end_idx] = reduced_chunk
                    
                    # Update progress bar
                    pbar.update(1)
        else:
            # Process the entire file at once
            reduced_noise = nr.reduce_noise(y=audio_data, y_noise=noise_sample, sr=sr)
        
        process_time = time.time() - start_time
        print(f"Noise reduction completed in {process_time:.2f} seconds")
        
        # Generate output file path
        base_dir = os.path.dirname(audio_file)
        base_name = os.path.basename(audio_file)
        name_without_ext, ext = os.path.splitext(base_name)
        output_file = os.path.join(base_dir, f"{name_without_ext}_denoised{ext}")
        
        # Ensure the output directory exists
        os.makedirs(base_dir, exist_ok=True)
        
        print(f"Saving processed audio to {output_file}")
        
        # Determine output format and apply appropriate compression
        if output_file.lower().endswith('.m4a'):
            # For M4A format, use workaround since ffmpeg might be missing
            # Save as compressed format
            mp3_output = output_file.replace('.m4a', '.mp3')
            print(f"Saving as compressed format instead of M4A: {mp3_output}")
            
            # Normalize audio to avoid clipping
            reduced_noise = reduced_noise / np.max(np.abs(reduced_noise) + 1e-8)
            
            try:
                # First try with pydub for better compression
                # Convert numpy array to AudioSegment for pydub processing
                audio_segment = AudioSegment(
                    (reduced_noise * 32767).astype(np.int16).tobytes(),
                    frame_rate=sr,
                    sample_width=2,  # 16-bit
                    channels=1 if len(reduced_noise.shape) == 1 else reduced_noise.shape[1]
                )
                
                # Export as MP3 with compression
                audio_segment.export(mp3_output, format="mp3", bitrate="128k")
                print("Successfully compressed audio using pydub.")
                
            except FileNotFoundError:
                # Fallback if ffmpeg is not available
                print("ffmpeg not found. Using alternative compression method.")
                
                # Save as WAV with reduced bit depth for better compatibility
                # This provides some compression compared to original
                wav_temp = output_file.replace('.m4a', '_temp.wav')
                
                # Apply additional compression techniques
                # 1. Convert to mono if not already
                if len(reduced_noise.shape) > 1:
                    reduced_noise = np.mean(reduced_noise, axis=1)
                    print("Converted to mono to reduce file size.")
                
                # 2. Save as 16-bit WAV (reduced from 32-bit float)
                sf.write(wav_temp, (reduced_noise * 32767).astype(np.int16), sr, subtype='PCM_16')
                
                # 3. For compatibility, rename to MP3
                if os.path.exists(mp3_output):
                    os.remove(mp3_output)
                shutil.copy(wav_temp, mp3_output)
                os.remove(wav_temp)
                
                print("Note: For better compression, please install ffmpeg.")
                print("Installation command example (Homebrew): brew install ffmpeg")
            
            # Update output_file to reflect the actual saved file
            output_file = mp3_output
        else:
            # For other formats, use soundfile with compression
            # Normalize audio to avoid clipping
            reduced_noise = reduced_noise / np.max(np.abs(reduced_noise) + 1e-8)
            
            # Use 16-bit encoding for better compression
            sf.write(output_file, (reduced_noise * 32767).astype(np.int16), sr, subtype='PCM_16')
        
        save_time = time.time() - start_time
        print(f"Audio saved successfully! Saving time: {save_time:.2f} seconds")
        
        # Report file size reduction
        output_size = os.path.getsize(output_file) / (1024 * 1024)  # Convert to MB
        print(f"Output file size: {output_size:.2f} MB")
        if 'raw_audio_file' in locals():
            raw_size = os.path.getsize(raw_audio_file) / (1024 * 1024)
            reduction = (raw_size - output_size) / raw_size * 100
            print(f"File size reduction: {reduction:.1f}%")
        
        return output_file
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        raise

def main():
    # Set download directory to user's Downloads folder
    download_dir = os.path.expanduser('~/Downloads')
    
    # Ensure download directory exists
    os.makedirs(download_dir, exist_ok=True)
    
    # Check if help flag is provided
    if len(sys.argv) > 1 and (sys.argv[1] == '--help' or sys.argv[1] == '-h'):
        print("=== YouTube Audio Download and Noise Reduction Tool ===")
        print("Usage:")
        print("  python download_process_audio.py [YouTube URL1] [YouTube URL2] ...")
        print("  If no URLs are provided, the tool will use default URLs.")
        print("")
        print("Description:")
        print("  This tool will:")
        print("  1. Download audio from the provided YouTube URLs")
        print("  2. Save the raw audio with '_raw' suffix")
        print("  3. Apply noise reduction to the audio")
        print("  4. Save the denoised version")
        print("")
        print("\nNotes:")
        print("  - All files are saved to your Downloads folder")
        print("  - Large files (>100MB) are processed in chunks for better performance")
        print("  - ffmpeg is required for audio processing")
        return
    
    # Check if URLs are provided as arguments
    if len(sys.argv) > 1:
        URLS = sys.argv[1:]
    else:
        # Default URLs if none provided
        URLS = [
            'https://www.youtube.com/watch?v=BUJpAzByMjo&t=279s'
        ]
    
    print("=== YouTube Audio Download and Noise Reduction Tool ===")
    print("This tool will download audio from YouTube, save the raw audio,")
    print("and immediately apply noise reduction, saving both versions.")
    print(f"Files will be saved to: {download_dir}")
    
    # Check if ffmpeg is installed
    try:
        # Try to find ffmpeg in PATH
        if os.system('which ffmpeg > /dev/null 2>&1') != 0:
            print("ERROR: ffmpeg is required but not detected!")
            print("Please install ffmpeg and try again.")
            print("Installation command example (Homebrew): brew install ffmpeg")
            sys.exit(1)
        print("ffmpeg installation detected")
    except Exception:
        print("ERROR: ffmpeg is required but error occurred during detection!")
        sys.exit(1)
    
    # Build output template path
    ydl_opts = {
        # Proxy configuration
        'proxy': 'http://127.0.0.1:7890',
        # Add SSL configuration
        'nocheckcertificate': True,
        # Increase retry count
        'retries': 10,
        # Set timeout
        'socket_timeout': 30,
        # Download audio format
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        # Use ffmpeg for audio extraction
        'postprocessors': [],
        # Set download directory
        'outtmpl': os.path.join(download_dir, '%(title)s [%(id)s].%(ext)s')
    }
    
    # Create a list to store downloaded file paths
    downloaded_files = []
    
    print(f"Starting audio download for {len(URLS)} video(s)...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Download each URL and track the files
            for url in URLS:
                print(f"\nDownloading audio from: {url}")
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                downloaded_files.append(filename)
                
                # Download the file
                error_code = ydl.download([url])
                
                if error_code == 0:
                    print(f"Audio downloaded successfully: {filename}")
                else:
                    print(f"Error occurred during audio download, error code: {error_code}")
                    downloaded_files.pop()  # Remove from list if download failed
            
            print("\n=== All downloads completed ===")
            
            # Process each downloaded file with noise reduction
            for audio_file in downloaded_files:
                print(f"\n=== Processing file: {os.path.basename(audio_file)} ===")
                try:
                    # Create a copy with '_raw' suffix to clearly identify raw audio
                    raw_audio_file = audio_file.replace('.', '_raw.')
                    if os.path.exists(raw_audio_file):
                        os.remove(raw_audio_file)
                    shutil.copy2(audio_file, raw_audio_file)
                    print(f"Raw audio saved as: {os.path.basename(raw_audio_file)}")
                    
                    # Apply noise reduction
                    denoised_file = reduce_noise(audio_file)
                    print(f"Denoised audio saved as: {os.path.basename(denoised_file)}")
                except Exception as e:
                    print(f"Failed to process {audio_file}: {str(e)}")
            
            print("\n=== All files processed ===")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    main()