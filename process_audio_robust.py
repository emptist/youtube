#!/usr/bin/env python3
import os
import sys
import glob
import time
import signal
import subprocess
from pathlib import Path

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Operation timed out")

def find_file_in_downloads(keyword):
    """
    Search for files containing the specified keyword in the Downloads folder
    """
    try:
        downloads_path = os.path.expanduser('~/Downloads')
        pattern = os.path.join(downloads_path, f'*{keyword}*')
        matches = glob.glob(pattern)
        # Normalize file paths to handle special characters
        normalized_matches = [os.path.normpath(match) for match in matches]
        return normalized_matches
    except Exception as e:
        print(f"Error searching for files: {str(e)}")
        return []

def list_audio_files():
    """
    List all audio files in the Downloads folder
    """
    try:
        downloads_path = os.path.expanduser('~/Downloads')
        audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
        audio_files = []
        
        for ext in audio_extensions:
            pattern = os.path.join(downloads_path, f'*{ext}')
            audio_files.extend(glob.glob(pattern))
            # Case-insensitive search
            pattern_lower = os.path.join(downloads_path, f'*{ext.lower()}')
            if ext.lower() != ext:
                audio_files.extend(glob.glob(pattern_lower))
        
        # Deduplicate and normalize
        audio_files = list(set([os.path.normpath(f) for f in audio_files]))
        return sorted(audio_files)
    except Exception as e:
        print(f"Error listing audio files: {str(e)}")
        return []

def run_noise_reduction(input_file, timeout=300):
    """
    Run noise reduction processing with timeout mechanism
    """
    try:
        # Ensure input file exists
        if not os.path.exists(input_file):
            print(f"Error: File '{input_file}' does not exist")
            return False
        
        # Generate output filename
        file_path = Path(input_file)
        output_file = str(file_path.parent / f"{file_path.stem}_denoised{file_path.suffix}")
        
        print(f"\nStarting file processing: {input_file}")
        print(f"Output file will be saved as: {output_file}")
        print(f"Timeout set to: {timeout} seconds")
        
        # Use subprocess to run noise reduction with timeout
        cmd = [
            sys.executable,
            '-c',
            f"import soundfile as sf; import librosa; import noisereduce as nr; import numpy as np;"
            f"audio_data, sr = librosa.load('{input_file}', sr=None);"
            f"noise_sample = audio_data[:int(2.0 * sr)];"
            f"reduced_noise = nr.reduce_noise(y=audio_data, y_noise=noise_sample, sr=sr);"
            f"sf.write('{output_file}', reduced_noise, sr)"
        ]
        
        # Using shell=False is safer, but requires proper handling of spaces and special characters in paths
        start_time = time.time()
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            shell=False
        )
        
        if result.returncode == 0:
            total_time = time.time() - start_time
            print(f"✅ Noise reduction processing complete!")
            print(f"Total time: {total_time:.2f} seconds")
            print(f"Processed file: {output_file}")
            return True
        else:
            print(f"❌ Processing failed, return code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Processing timed out, exceeded {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        return False

def create_alternative_script(file_path):
    """
    Create an alternative script that processes files in a simpler way
    """
    try:
        alt_script_path = 'process_simple.py'
        content = f"""
import soundfile as sf
import librosa
import noisereduce as nr
import numpy as np
import os

# Simple audio noise reduction script
input_file = '{file_path}'
print(f"Processing file: {{input_file}}")

# Ensure file exists
if not os.path.exists(input_file):
    print(f"Error: File '{{input_file}}' does not exist")
else:
    try:
        # Load audio file
        print("Loading audio...")
        audio_data, sr = librosa.load(input_file, sr=None)
        print(f"Audio loaded successfully: {{len(audio_data)/sr:.2f}} seconds, {{sr}}Hz")
        
        # Extract noise sample (first 2 seconds)
        noise_duration = 2.0
        noise_sample = audio_data[:int(noise_duration * sr)]
        
        # Apply noise reduction
        print("Applying noise reduction...")
        reduced_noise = nr.reduce_noise(y=audio_data, y_noise=noise_sample, sr=sr)
        
        # Save processed audio
        from pathlib import Path
        file_path = Path(input_file)
        output_file = str(file_path.parent / f"{{file_path.stem}}_denoised{{file_path.suffix}}")
        
        print(f"Saving processed audio to: {{output_file}}")
        sf.write(output_file, reduced_noise, sr)
        print("✅ Processing complete!")
        
    except Exception as e:
        print(f"Processing error: {{str(e)}}")
        import traceback
        traceback.print_exc()
"""
        
        with open(alt_script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Alternative script created: {alt_script_path}")
        print(f"You can try running: python {alt_script_path}")
        return alt_script_path
    except Exception as e:
        print(f"Error creating alternative script: {str(e)}")
        return None

def main():
    print("=== Robust Audio Noise Reduction Tool ===")
    print("This tool provides more stable audio noise processing functionality")
    print("\nUsage:")
    print("1. Run this script directly and it will display a list of processable audio files")
    print("2. Or specify a file path: python process_audio_robust.py /path/to/your/audio/file.m4a")
    print("\nNote: This version enhances handling of paths with special characters and adds timeout mechanism")
    
    # Check if there are command line arguments
    if len(sys.argv) > 1:
        # User provided a file path
        input_file = os.path.expanduser(sys.argv[1])
        
        # Try to process directly
        success = run_noise_reduction(input_file)
        
        if not success:
            print("\nAttempting to process with alternative method...")
            alt_script = create_alternative_script(input_file)
    else:
        # Display all audio files in Downloads folder
        print("\nScanning for audio files in Downloads folder...")
        audio_files = list_audio_files()
        
        if not audio_files:
            print("❌ No audio files found")
            return
        
        print(f"✅ Found {len(audio_files)} audio files:")
        for i, file_path in enumerate(audio_files, 1):
            # Display file size and modification time
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            mod_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(file_path)))
            print(f"{i}. {os.path.basename(file_path)} ({file_size:.2f} MB, {mod_time})")
            print(f"   Path: {file_path}")
        
        try:
            choice = input("\nEnter the file number to process (or press Enter to exit): ")
            if choice.strip():
                index = int(choice) - 1
                if 0 <= index < len(audio_files):
                    selected_file = audio_files[index]
                    print(f"\nYou selected: {selected_file}")
                    
                    # Run noise reduction processing
                    success = run_noise_reduction(selected_file)
                    
                    if not success:
                        print("\nAttempting to process with alternative method...")
                        alt_script = create_alternative_script(selected_file)
                else:
                    print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")
    
    print("\n💡 Tips:")
    print("1. If timeout occurs when processing large files, you can modify the timeout parameter in the script")
    print("2. If filenames contain special characters, it's recommended to rename them first")
    print("3. You can also try specifying the file path directly via command line")

if __name__ == "__main__":
    main()