
import soundfile as sf
import librosa
import noisereduce as nr
import numpy as np
import os

# Simple audio noise reduction script
input_file = '/Users/jk/Downloads/dump1.mp3'
print(f"Processing file: {input_file}")

# Ensure file exists
if not os.path.exists(input_file):
    print(f"Error: File '{input_file}' does not exist")
else:
    try:
        # Load audio file
        print("Loading audio...")
        audio_data, sr = librosa.load(input_file, sr=None)
        print(f"Audio loaded successfully: {len(audio_data)/sr:.2f} seconds, {sr}Hz")
        
        # Extract noise sample (first 2 seconds)
        noise_duration = 2.0
        noise_sample = audio_data[:int(noise_duration * sr)]
        
        # Apply noise reduction
        print("Applying noise reduction...")
        reduced_noise = nr.reduce_noise(y=audio_data, y_noise=noise_sample, sr=sr)
        
        # Save processed audio
        from pathlib import Path
        file_path = Path(input_file)
        output_file = str(file_path.parent / f"{file_path.stem}_denoised{file_path.suffix}")
        
        print(f"Saving processed audio to: {output_file}")
        sf.write(output_file, reduced_noise, sr)
        print("✅ Processing complete!")
        
    except Exception as e:
        print(f"Processing error: {str(e)}")
        import traceback
        traceback.print_exc()
