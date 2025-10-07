import os
import sys
import time
import os
from de_noise import reduce_noise

if __name__ == "__main__":
    print("=== Audio Noise Reduction Tool ===")
    print("This script will process the specified audio file to reduce background noise")
    print("\nPreparing for processing...")
    
    # Audio file path mentioned by user
    audio_file = os.path.expanduser('~/Downloads/Lojong2TrainingTheMind-JetsunKhandroRinpoche2/2.m4a')
    
    print(f"Target file: {audio_file}")
    
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"Error: File '{audio_file}' does not exist.")
        print("Please confirm the file path is correct, or modify the file path in the script.")
        print("\nYou can also try specifying the file path directly:")
        print(f"python {os.path.basename(sys.argv[0])} /path/to/your/audio/file.m4a")
    else:
        try:
            total_start_time = time.time()
            
            # For large files, you can adjust the chunk_duration parameter
            # Default 30-second chunk processing should work for most files
            print("\nStarting file processing...")
            print("- Processing progress bar and timing for each stage will be displayed")
            print("- Processing may take some time for large files")
            print("- Press Ctrl+C to interrupt processing at any time")
            print("\n----------------------------------")
            
            # Call noise reduction function with default parameters
            # For large files, you can add parameter: chunk_duration=60 (or other suitable value)
            output_file = reduce_noise(audio_file)
            
            total_time = time.time() - total_start_time
            
            print("\n----------------------------------")
            print(f"\n✅ Noise reduction processing complete!")
            print(f"Total time: {total_time:.2f} seconds")
            print(f"Original file: {audio_file}")
            print(f"Processed file: {output_file}")
            print("\n💡 Tips:")
            print("1. The processed file is saved in the same directory as the original file with '_denoised' suffix")
            print("2. You can compare the audio quality between the original and processed files")
            print("3. If you're not satisfied with the results, you can adjust the following parameters:")
            print("   - noise_sample_duration: Noise sample duration (default 2 seconds)")
            print("   - chunk_duration: Chunk processing duration (default 30 seconds)")
            print("4. You can also use the command line tool for more control:")
            print("   python de_noise.py -h")
        except KeyboardInterrupt:
            print("\n⚠️ Processing interrupted by user.")
        except Exception as e:
            print(f"❌ Processing failed: {str(e)}")
            print("Please check the error message and try to resolve the issue.")