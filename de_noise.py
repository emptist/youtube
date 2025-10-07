import os
import sys
import numpy as np
import librosa
import noisereduce as nr
from pathlib import Path
import argparse
from tqdm import tqdm
import subprocess
import time

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


def reduce_noise(input_file, output_file=None, noise_sample_duration=2.0, chunk_duration=30):
    """
    Reduce noise in an audio file
    
    Parameters:
    input_file: Input audio file path
    output_file: Output audio file path, if None will add '_denoised' to the original filename
    noise_sample_duration: Duration for noise sampling (seconds), default first 2 seconds
    chunk_duration: Duration for chunk processing (seconds), useful for large files
    """
    try:
        # Load audio file
        print(f"Loading audio file: {input_file}")
        start_time = time.time()
        
        # For large files, load with mono=True and offset/duration parameters for faster loading
        # Check file size first
        file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
        
        # For files over 100MB, use optimized loading settings
        if file_size_mb > 100:
            print(f"Large file detected ({file_size_mb:.2f} MB), using optimized loading settings")
            # For very large files, load as mono to reduce memory usage
            audio_data, sr = librosa.load(input_file, sr=None, mono=True)
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
                    reduced_chunk = nr.reduce_noise(y=chunk, y_noise=noise_sample, sr=sr)
                    reduced_noise[start_idx:end_idx] = reduced_chunk
                    
                    pbar.update(1)
        else:
            # Process all at once
            with tqdm(total=1, desc="Processing progress") as pbar:
                reduced_noise = nr.reduce_noise(y=audio_data, y_noise=noise_sample, sr=sr)
                pbar.update(1)
        
        process_time = time.time() - start_time
        print(f"Noise reduction completed, processing time: {process_time:.2f} seconds")
        
        # Determine output filename
        if output_file is None:
            file_path = Path(input_file)
            output_file = str(file_path.parent / f"{file_path.stem}_denoised{file_path.suffix}")
        
        # Ensure output directory exists
        os.makedirs(Path(output_file).parent, exist_ok=True)
        
        # Save processed audio
        print(f"Saving processed audio to: {output_file}")
        start_time = time.time()
        
        # Save processed audio using soundfile
        import soundfile as sf
        sf.write(output_file, reduced_noise, sr)
        
        save_time = time.time() - start_time
        print(f"Audio saved successfully! Saving time: {save_time:.2f} seconds")
        
        return output_file
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        raise


def main():
    # Create command line argument parser
    parser = argparse.ArgumentParser(description='Audio Noise Reduction Tool')
    parser.add_argument('input_file', help='Input audio file path')
    parser.add_argument('-o', '--output', help='Output audio file path', default=None)
    parser.add_argument('-d', '--duration', type=float, default=2.0, 
                        help='Duration for noise sampling (seconds), default first 2 seconds')
    parser.add_argument('-c', '--chunk', type=float, default=30, 
                        help='Duration for chunk processing (seconds), useful for large files, default 30 seconds')
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Expand user directory symbol
    input_file = os.path.expanduser(args.input_file)
    output_file = os.path.expanduser(args.output) if args.output else None
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist")
        return
    
    # Execute noise reduction
    reduce_noise(input_file, output_file, args.duration, args.chunk)


if __name__ == "__main__":
    # If running the script directly, execute the main function
    main()
    
    # You can also add test code here, for example:
# if __name__ == "__main__":
#     # Process a specific file directly
#     input_path = os.path.expanduser('~/Downloads/Lojong2TrainingTheMind-JetsunKhandroRinpoche2/2.m4a')
#     reduce_noise(input_path)