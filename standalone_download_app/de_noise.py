import sys
import os
from pathlib import Path
import argparse
import subprocess
import time
import signal

# Import TimeoutException from process_audio_robust.py
# Check if we can import it from the module
can_import_timeout_exception = False

try:
    # Try importing TimeoutException
    from process_audio_robust import TimeoutException
    can_import_timeout_exception = True
except ImportError:
    # Define a local version if import fails
    class TimeoutException(Exception):
        """Exception raised when an operation times out"""
        pass

# Define timeout handler if not already defined in the imported module
def timeout_handler(signum, frame):
    raise TimeoutException("Operation timed out")

# Lazy import function for heavy libraries
def _import_heavy_libraries():
    """Lazily import heavy libraries when needed"""
    import numpy as np
    import librosa
    import noisereduce as nr
    import soundfile as sf
    from tqdm import tqdm
    return np, librosa, nr, sf, tqdm

# Add the parent directory to Python path to import ffmpeg_utils
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the shared ffmpeg utility
from ffmpeg_utils import check_ffmpeg as _check_ffmpeg


def reduce_noise(
    input_file: str,
    output_file: str = None,
    noise_sample_duration: float = 2.0,
    chunk_duration: float = 30.0
):
    """Apply noise reduction to an audio file.
    
    Args:
        input_file: Input audio file path
        output_file: Output audio file path, if None will add '_denoised' to the original filename
        noise_sample_duration: Duration for noise sampling (seconds), default first 2 seconds
        chunk_duration: Duration for chunk processing (seconds), useful for large files
    """
    try:
        # Check if ffmpeg is installed
        ffmpeg_installed, ffmpeg_msg = _check_ffmpeg()
        if not ffmpeg_installed:
            raise RuntimeError(ffmpeg_msg)
        
        # Import heavy libraries only when needed
        np, librosa, nr_lib, sf, tqdm = _import_heavy_libraries()
        
        # Save original file path before any potential conversion
        original_input_file = input_file
        
        # Load audio file
        print(f"Loading audio file: {input_file}")
        start_time = time.time()
        
        # For large files, load with mono=True and offset/duration parameters for faster loading
        # Check file size first
        file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
        
        # Show loading feedback
        print(f"File size: {file_size_mb:.2f} MB")
        
        # Check if file is M4A format
        is_m4a = input_file.lower().endswith('.m4a')
        
        if is_m4a:
            print(f"M4A format detected. Converting to WAV temporarily using ffmpeg for better compatibility...")
            
            # Create temporary WAV file for processing
            temp_wav = str(Path(input_file).parent / f"{Path(input_file).stem}_temp.wav")
            
            # Use ffmpeg to convert M4A to WAV
            try:
                print(f"Converting {input_file} to {temp_wav}")
                subprocess.run([
                    'ffmpeg', '-y', '-i', input_file,
                    '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '1', temp_wav
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Set input_file to the temporary WAV file
                input_file = temp_wav
            except subprocess.CalledProcessError as e:
                print(f"ERROR: Failed to convert M4A to WAV: {str(e)}")
                raise
        
        # For files over 100MB, use optimized loading settings and implement timeout
        if file_size_mb > 100:
            print(f"Large file detected ({file_size_mb:.2f} MB), using optimized loading settings")
            
            # Set loading timeout (adjust as needed) - more time for M4A files
            loading_timeout = max(120, int(file_size_mb / 5))  # At least 120s, more for larger files
            if is_m4a:
                loading_timeout = max(loading_timeout, 300)  # Extra time for M4A conversion
            print(f"Loading timeout set to {loading_timeout} seconds")
            
            # Implement timeout mechanism if we can
            if can_import_timeout_exception:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(loading_timeout)
                
            try:
                # For very large files, load as mono to reduce memory usage
                audio_data, sr = librosa.load(input_file, sr=None, mono=True)
                
                # Clear alarm if loading completed within timeout
                if can_import_timeout_exception:
                    signal.alarm(0)
            except TimeoutException:
                print("ERROR: Audio file loading timed out. The file may be too large or corrupted.")
                print("You can try splitting the file into smaller segments first.")
                # Clean up temporary file if it exists
                if is_m4a and os.path.exists(temp_wav):
                    os.remove(temp_wav)
                if can_import_timeout_exception:
                    signal.alarm(0)  # Clear alarm
                raise
            finally:
                # Ensure alarm is cleared
                if can_import_timeout_exception:
                    signal.alarm(0)
        else:
            audio_data, sr = librosa.load(input_file, sr=None)
            
        load_time = time.time() - start_time
        print(f"Audio loaded successfully, sample rate: {sr} Hz, duration: {len(audio_data)/sr:.2f} seconds")
        print(f"Loading time: {load_time:.2f} seconds")
        print(f"File size: {file_size_mb:.2f} MB")
        
        # Process large file notification
        if file_size_mb > 100:
            print("Note: Large file detected, processing may take some time.")
        
        # Use the first noise_sample_duration seconds as noise sample
        noise_sample = audio_data[:int(noise_sample_duration * sr)]
        
        # Apply noise reduction with progress feedback
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
                    reduced_chunk = nr_lib.reduce_noise(y=chunk, y_noise=noise_sample, sr=sr)
                    reduced_noise[start_idx:end_idx] = reduced_chunk
                    
                    pbar.update(1)
        else:
            # Process all at once
            with tqdm(total=1, desc="Processing progress") as pbar:
                reduced_noise = nr_lib.reduce_noise(y=audio_data, y_noise=noise_sample, sr=sr)
                pbar.update(1)
        
        process_time = time.time() - start_time
        print(f"Noise reduction completed, processing time: {process_time:.2f} seconds")
        
        # Determine output filename
        if output_file is None:
            # Use original file path to ensure correct extension
            file_path = Path(original_input_file)
            output_file = str(file_path.parent / f"{file_path.stem}_denoised{file_path.suffix}")
        
        # Ensure output directory exists
        os.makedirs(Path(output_file).parent, exist_ok=True)
        
        # Save processed audio
        print(f"Saving processed audio to: {output_file}")
        start_time = time.time()
        
        # For M4A files, we need to convert the processed WAV back to M4A
        if is_m4a:
            # First save as WAV temporarily
            temp_output_wav = output_file.replace('.m4a', '_temp.wav')
            
            # Save processed audio as WAV
            sf.write(temp_output_wav, reduced_noise, sr)
            
            # Then convert to M4A using ffmpeg
            try:
                print(f"Converting processed WAV to M4A: {output_file}")
                subprocess.run([
                    'ffmpeg', '-y', '-i', temp_output_wav,
                    '-c:a', 'aac', '-strict', 'experimental',
                    '-b:a', '128k', output_file
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Only clean up temporary files after successful conversion
                if os.path.exists(temp_wav):
                    os.remove(temp_wav)  # Delete the original input temp file
                if os.path.exists(temp_output_wav):
                    os.remove(temp_output_wav)  # Delete the processed temp file
            except subprocess.CalledProcessError as e:
                print(f"ERROR: Failed to convert processed audio to M4A: {str(e)}")
                # For failed conversion, keep the processed WAV file so user can retry conversion
                # Only remove the original input temp file
                if os.path.exists(temp_wav):
                    os.remove(temp_wav)
                print(f"NOTE: Processed WAV file has been kept at: {temp_output_wav}")
                print(f"      You can manually convert it to M4A with: ffmpeg -i {temp_output_wav} -c:a aac -strict experimental -b:a 128k {output_file}")
                raise
        else:
            # For other formats, use soundfile directly
            sf.write(output_file, reduced_noise, sr)
        
        save_time = time.time() - start_time
        print(f"Audio saved successfully! Saving time: {save_time:.2f} seconds")
        
        return output_file
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        # Clean up temporary files if they exist
        if 'is_m4a' in locals() and is_m4a:
            if 'temp_wav' in locals() and os.path.exists(temp_wav):
                os.remove(temp_wav)
            if 'temp_output_wav' in locals() and os.path.exists(temp_output_wav):
                os.remove(temp_output_wav)
        raise


def main():
    # Create command line argument parser
    parser = argparse.ArgumentParser(description='Audio Noise Reduction Tool')
    parser.add_argument('input_file', help='Input audio file path')
    parser.add_argument('-o', '--output', help='Output audio file path', default=None)
    parser.add_argument('-n', '--noise-duration', type=float, default=2.0, 
                        help='Duration for noise sampling (seconds), default first 2 seconds')
    parser.add_argument('-c', '--chunk-duration', type=float, default=30.0, 
                        help='Duration for chunk processing (seconds), useful for large files')
    
    # Parse command line arguments
    args = parser.parse_args()
    
    try:
        # Call the noise reduction function
        output_file = reduce_noise(
            args.input_file,
            output_file=args.output,
            noise_sample_duration=args.noise_duration,
            chunk_duration=args.chunk_duration
        )
        
        print(f"Noise reduction completed successfully!")
        print(f"Output file: {output_file}")
        sys.exit(0)
    except Exception as e:
        print(f"Noise reduction failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()