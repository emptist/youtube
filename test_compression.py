#!/usr/bin/env python3
import os
import numpy as np
import soundfile as sf
import tempfile
import shutil
import sys

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

# Import required libraries
from pydub import AudioSegment
print("pydub library loaded successfully.")

# Create a temporary directory for testing
temp_dir = tempfile.mkdtemp()
print(f"Created temporary directory for testing: {temp_dir}")

try:
    # Generate a test audio signal
    print("\nGenerating test audio signal...")
    duration = 10  # seconds
    sample_rate = 44100
    freq = 440  # Hz (A4 note)
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Create a complex audio signal with multiple frequencies
    audio = np.sin(2 * np.pi * freq * t)  # Fundamental frequency
    audio += 0.5 * np.sin(2 * np.pi * 2 * freq * t)  # Second harmonic
    audio += 0.3 * np.sin(2 * np.pi * 3 * freq * t)  # Third harmonic
    
    # Add some noise
    noise = 0.1 * np.random.randn(len(audio))
    audio_with_noise = audio + noise
    
    # Save original 32-bit float WAV (uncompressed)
    original_file = os.path.join(temp_dir, "original_32bit.wav")
    sf.write(original_file, audio_with_noise, sample_rate)
    original_size = os.path.getsize(original_file) / (1024 * 1024)  # Convert to MB
    print(f"Original 32-bit float WAV saved: {original_size:.2f} MB")
    
    # Test 1: Basic 16-bit conversion (foundation for all compression)
    print("\n=== Testing 16-bit Conversion ===")
    # Normalize audio
    normalized_audio = audio_with_noise / (np.max(np.abs(audio_with_noise)) + 1e-8)
    
    # Convert to 16-bit integer
    audio_16bit = (normalized_audio * 32767).astype(np.int16)
    
    # Save as 16-bit WAV
    compressed_wav_file = os.path.join(temp_dir, "compressed_16bit.wav")
    sf.write(compressed_wav_file, audio_16bit, sample_rate, subtype='PCM_16')
    compressed_wav_size = os.path.getsize(compressed_wav_file) / (1024 * 1024)  # Convert to MB
    wav_compression_ratio = (original_size - compressed_wav_size) / original_size * 100
    print(f"Compressed 16-bit WAV: {compressed_wav_size:.2f} MB (Reduction: {wav_compression_ratio:.1f}%)")
    
    # Test 2: Pydub compression with ffmpeg
    print("\n=== Testing Pydub Compression ===")
    try:
        # Convert numpy array to AudioSegment
        audio_segment = AudioSegment(
            audio_16bit.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,  # 16-bit
            channels=1  # Mono
        )
        
        # Export as MP3 with compression
        mp3_new_method = os.path.join(temp_dir, "mp3_new_method.mp3")
        audio_segment.export(mp3_new_method, format="mp3", bitrate="128k")
        mp3_new_size = os.path.getsize(mp3_new_method) / (1024 * 1024)  # Convert to MB
        new_mp3_compression_ratio = (original_size - mp3_new_size) / original_size * 100
        print(f"Pydub MP3 compression: {mp3_new_size:.2f} MB (Reduction: {new_mp3_compression_ratio:.1f}%)")
        print("Successfully used pydub for MP3 compression.")
    except Exception as e:
        print(f"Pydub compression failed: {str(e)}")
    
    # Summary of compression methods
    print("\n=== Compression Method Summary ===")
    print(f"Original 32-bit float WAV:      {original_size:.2f} MB")
    print(f"16-bit Conversion:             {compressed_wav_size:.2f} MB (Reduction: {wav_compression_ratio:.1f}%)")
    print(f"Pydub MP3:                     {mp3_new_size:.2f} MB (Reduction: {new_mp3_compression_ratio:.1f}%)")
    
    # Now test with the download_process_audio.py module if available
    try:
        print("\n=== Testing with download_process_audio.py ===")
        sys.path.append(".")
        
        # Test the compression function
        from download_process_audio import reduce_noise
        
        # Create a M4A test file by copying (just for testing the extension handling)
        test_m4a_file = os.path.join(temp_dir, "test_file.m4a")
        shutil.copy(original_file, test_m4a_file)
        
        print("Testing the updated reduce_noise function with M4A workaround...")
        # This will trigger our updated compression code
        denoised_file = reduce_noise(test_m4a_file, noise_duration=1.0, chunk_duration=5)
        
        # Check the file size of the denoised output
        denoised_size = os.path.getsize(denoised_file) / (1024 * 1024)  # Convert to MB
        denoised_reduction = (original_size - denoised_size) / original_size * 100
        
        print(f"Test completed successfully!")
        print(f"Denoised file saved to: {denoised_file}")
        print(f"Denoised file size: {denoised_size:.2f} MB (Reduction: {denoised_reduction:.1f}%)")
        
    except Exception as e:
        print(f"Could not fully test with download_process_audio.py: {str(e)}")
        print("However, the basic compression test results above still demonstrate the available compression methods.")
        
finally:
    # Clean up temporary files
    print(f"\nCleaning up temporary files...")
    shutil.rmtree(temp_dir)
    print("Test completed.")