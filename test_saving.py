#!/usr/bin/env python3
import os
import sys
import numpy as np
import librosa
import soundfile as sf
import argparse
import subprocess

# Ensure we can import ffmpeg_utils even when running from different locations
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the shared ffmpeg utility
from ffmpeg_utils import check_ffmpeg

# Check if ffmpeg is installed
success, message = check_ffmpeg()
if not success:
    print(f"ERROR: {message}")
    sys.exit(1)

print(message)

"""
Helper script to test M4A audio saving functionality.
This script can load a small segment of audio and save it in M4A format.
Useful for testing without reprocessing entire large files.
"""

def save_sample_audio(input_file, output_file, sample_duration=10):
    """
    Load a small sample of audio and save it in M4A format.
    
    Parameters:
    input_file: Path to input audio file
    output_file: Path to save the test M4A file
    sample_duration: Duration of sample to extract (seconds)
    """
    try:
        print(f"Loading {sample_duration} seconds from {input_file}")
        
        # Load only a sample of the audio to save time
        audio_data, sr = librosa.load(
            input_file, 
            sr=None, 
            mono=True,  # Load as mono for faster processing
            duration=sample_duration  # Only load a small segment
        )
        
        print(f"Loaded audio sample, sample rate: {sr} Hz")
        
        # Ensure the audio data is in the correct range (-1 to 1)
        if np.max(np.abs(audio_data)) > 1.0:
            audio_data = audio_data / np.max(np.abs(audio_data))
            print("Normalized audio data to range [-1, 1]")
        
        # Use appropriate method based on file format
        if output_file.lower().endswith('.m4a'):
            # For M4A format, use ffmpeg for conversion
            print(f"Saving test M4A file: {output_file}")
            
            # First save as WAV temporarily
            wav_temp = output_file.replace('.m4a', '.wav')
            sf.write(wav_temp, audio_data, sr)
            
            # Then convert to M4A using ffmpeg
            try:
                subprocess.run([
                    'ffmpeg', '-y', '-i', wav_temp,
                    '-c:a', 'aac', '-strict', 'experimental',
                    '-b:a', '128k', output_file
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"Successfully saved test M4A file: {output_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error converting to M4A: {str(e)}")
                raise
            finally:
                # Clean up temporary file
                if os.path.exists(wav_temp):
                    os.remove(wav_temp)
        else:
            # For other formats, use soundfile directly
            sf.write(output_file, audio_data, sr)
            print(f"Successfully saved test audio file: {output_file}")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Test M4A audio saving functionality')
    parser.add_argument('input_file', help='Input audio file path')
    parser.add_argument('-o', '--output', help='Output M4A file path', default=None)
    parser.add_argument('-d', '--duration', type=float, default=10, 
                        help='Duration of sample to extract (seconds), default 10')
    
    args = parser.parse_args()
    
    # Expand user directory symbol
    input_file = os.path.expanduser(args.input_file)
    
    # Set default output if not specified
    if args.output is None:
        from pathlib import Path
        file_path = Path(input_file)
        output_file = str(file_path.parent / f"{file_path.stem}_test{file_path.suffix}")
    else:
        output_file = os.path.expanduser(args.output)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Run the test
    save_sample_audio(input_file, output_file, args.duration)

if __name__ == "__main__":
    main()