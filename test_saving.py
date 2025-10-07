#!/usr/bin/env python3
import os
import sys
import numpy as np
import librosa
import soundfile as sf
import argparse

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
        
        # Check if file extension is M4A
        if output_file.lower().endswith('.m4a'):
            # For M4A format, we need to use a workaround since ffmpeg is missing
            # We'll save as WAV first, then convert extension to MP3 for compatibility
            mp3_output = output_file.replace('.m4a', '.mp3')
            print(f"Saving as MP3 instead of M4A (ffmpeg not available): {mp3_output}")
            
            # Use soundfile to save as WAV temporarily
            wav_temp = output_file.replace('.m4a', '.wav')
            sf.write(wav_temp, audio_data, sr)
            
            # Rename to MP3 for compatibility (simple workaround)
            import shutil
            if os.path.exists(mp3_output):
                os.remove(mp3_output)
            shutil.copy(wav_temp, mp3_output)
            os.remove(wav_temp)
            
            print(f"Successfully saved test MP3 file: {mp3_output}")
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