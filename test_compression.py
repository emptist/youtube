#!/usr/bin/env python3
import os
import numpy as np
import soundfile as sf
import tempfile
import shutil
import sys

# Try to import pydub but handle if it's not available
try:
    from pydub import AudioSegment
    pydub_available = True
    print("pydub library loaded successfully.")
except ImportError:
    pydub_available = False
    print("pydub library not available. Will test alternative compression methods.")

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
    
    # Test 2: Old method - simple file copy
    print("\n=== Testing Old Method (File Copy) ===")
    mp3_old_method = os.path.join(temp_dir, "mp3_old_method.mp3")
    if os.path.exists(mp3_old_method):
        os.remove(mp3_old_method)
    shutil.copy(compressed_wav_file, mp3_old_method)
    mp3_old_size = os.path.getsize(mp3_old_method) / (1024 * 1024)  # Convert to MB
    old_mp3_compression_ratio = (original_size - mp3_old_size) / original_size * 100
    print(f"Old MP3 workaround (copy): {mp3_old_size:.2f} MB (Reduction: {old_mp3_compression_ratio:.1f}%)")
    
    # Test 3: Alternative compression - convert to mono and 16-bit (new fallback method)
    print("\n=== Testing Alternative Compression (Mono + 16-bit) ===")
    # Ensure it's mono
    if len(audio_with_noise.shape) > 1:
        mono_audio = np.mean(audio_with_noise, axis=1)
    else:
        mono_audio = audio_with_noise.copy()
    
    # Normalize and convert to 16-bit
    normalized_mono = mono_audio / (np.max(np.abs(mono_audio)) + 1e-8)
    mono_16bit = (normalized_mono * 32767).astype(np.int16)
    
    # Save as WAV then rename to MP3
    alt_temp_file = os.path.join(temp_dir, "alt_temp.wav")
    sf.write(alt_temp_file, mono_16bit, sample_rate, subtype='PCM_16')
    
    alt_mp3_file = os.path.join(temp_dir, "alternative_compression.mp3")
    if os.path.exists(alt_mp3_file):
        os.remove(alt_mp3_file)
    shutil.copy(alt_temp_file, alt_mp3_file)
    os.remove(alt_temp_file)
    
    alt_mp3_size = os.path.getsize(alt_mp3_file) / (1024 * 1024)  # Convert to MB
    alt_compression_ratio = (original_size - alt_mp3_size) / original_size * 100
    print(f"Alternative compression (mono + 16-bit): {alt_mp3_size:.2f} MB (Reduction: {alt_compression_ratio:.1f}%)")
    
    # Test 4: Try pydub compression if available
    mp3_new_size = None
    new_mp3_compression_ratio = None
    
    if pydub_available:
        print("\n=== Testing Pydub Compression (if ffmpeg is available) ===")
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
        except FileNotFoundError:
            print("ffmpeg not found. Pydub compression requires ffmpeg.")
            print("For better compression, please install ffmpeg.")
            print("Installation command example (Homebrew): brew install ffmpeg")
        except Exception as e:
            print(f"Pydub compression failed: {str(e)}")
    
    # Summary of compression methods
    print("\n=== Compression Method Summary ===")
    print(f"Original 32-bit float WAV:      {original_size:.2f} MB")
    print(f"16-bit Conversion:             {compressed_wav_size:.2f} MB (Reduction: {wav_compression_ratio:.1f}%)")
    print(f"Old Method (File Copy):         {mp3_old_size:.2f} MB (Reduction: {old_mp3_compression_ratio:.1f}%)")
    print(f"Alternative (Mono + 16-bit):    {alt_mp3_size:.2f} MB (Reduction: {alt_compression_ratio:.1f}%)")
    if mp3_new_size is not None:
        print(f"Pydub MP3 (with ffmpeg):       {mp3_new_size:.2f} MB (Reduction: {new_mp3_compression_ratio:.1f}%)")
    
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