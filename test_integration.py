#!/usr/bin/env python3
import os
import sys
import shutil
import numpy as np
import soundfile as sf
import librosa
import time

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

# This is a simplified test script to verify the download_process_audio.py concept
# without actually downloading from YouTube

def main():
    print("=== Testing Audio Processing Integration ===")
    
    # Create a temporary test audio file
    # This would be replaced with actual YouTube download in the real script
    test_dir = os.path.expanduser('~/Downloads')
    test_file = os.path.join(test_dir, "test_integration_audio.m4a")
    
    try:
        # For this test, we'll check if there's an existing audio file to work with
        # We'll look for the sample file mentioned in previous tests
        sample_file = "Lojong2-JetsunKhandro.m4a"
        sample_path = os.path.join(test_dir, sample_file)
        
        if os.path.exists(sample_path):
            print(f"Found sample audio file: {sample_file}")
            # Copy it to our test file
            shutil.copy2(sample_path, test_file)
            print(f"Created test file: {test_file}")
        else:
            print(f"Sample file not found: {sample_file}")
            print("Creating a simple test audio file instead...")
            # Create a simple sine wave for testing
            sr = 44100  # Sample rate
            duration = 10  # 10 seconds
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            # Create a 440Hz sine wave
            audio = np.sin(2 * np.pi * 440 * t)
            # Add some "noise"
            noise = 0.1 * np.random.randn(len(t))
            noisy_audio = audio + noise
            
            # Save as WAV first (since we can't save M4A directly)
            wav_test_file = test_file.replace('.m4a', '.wav')
            sf.write(wav_test_file, noisy_audio, sr)
            # For the test, just keep it as WAV since we can't convert to M4A without ffmpeg
            test_file = wav_test_file
            print(f"Created test file with sine wave + noise: {test_file}")
        
        # Now simulate the workflow: save raw copy and process
        base_name = os.path.basename(test_file)
        name_without_ext, ext = os.path.splitext(base_name)
        
        # Save raw version
        raw_file = os.path.join(test_dir, f"{name_without_ext}_raw{ext}")
        if os.path.exists(raw_file):
            os.remove(raw_file)
        shutil.copy2(test_file, raw_file)
        print(f"Raw audio saved as: {os.path.basename(raw_file)}")
        
        # Simulate noise reduction
        print("Simulating noise reduction...")
        start_time = time.time()
        
        # Load the audio
        try:
            audio_data, sr = librosa.load(test_file, sr=None)
        except:
            audio_data, sr = sf.read(test_file)
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)  # Convert to mono
        
        # For this test, we'll just normalize the audio as a simple "processing"
        # In the real script, this would be the actual noise reduction
        processed_audio = audio_data / np.max(np.abs(audio_data))
        
        # Save processed version
        processed_file = os.path.join(test_dir, f"{name_without_ext}_denoised{ext}")
        
        # Save processed audio directly
        sf.write(processed_file, processed_audio, sr)
        
        process_time = time.time() - start_time
        print(f"Audio processing completed in {process_time:.2f} seconds")
        print(f"Denoised audio saved as: {os.path.basename(processed_file)}")
        
        print("\n=== Test Summary ===")
        print(f"1. Raw audio file: {os.path.basename(raw_file)}")
        print(f"2. Processed audio file: {os.path.basename(processed_file)}")
        print("\nThe download_process_audio.py script follows this same workflow but")
        print("additionally downloads the audio from YouTube first.")
        print("\nTo use it with actual YouTube URLs:")
        print("  python download_process_audio.py 'https://www.youtube.com/watch?v=VIDEO_ID'")
        print("\nMake sure to enclose URLs in quotes to avoid shell interpretation issues.")
            
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up temporary files if we created them
        if not os.path.exists(sample_path) and os.path.exists(test_file):
            try:
                os.remove(test_file)
                print(f"Cleaned up test file: {test_file}")
            except:
                pass

if __name__ == "__main__":
    main()