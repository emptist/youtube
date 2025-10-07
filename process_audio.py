#!/usr/bin/env python3
import os
import sys
import glob
import time
from de_noise import reduce_noise

def find_file_in_downloads(keyword):
    """
    Search for files containing the specified keyword in the Downloads folder
    """
    downloads_path = os.path.expanduser('~/Downloads')
    pattern = os.path.join(downloads_path, f'*{keyword}*')
    matches = glob.glob(pattern)
    return matches

def main():
    print("=== Audio Noise Reduction Tool ===")
    print("This tool will help you process the specified audio file to reduce background noise")
    print("\nUsage:")
    print("1. Run this script directly and it will try to search for files automatically")
    print("2. Or specify a file path: python process_audio.py /path/to/your/audio/file.m4a")
    
    # Check if there are command line arguments
    if len(sys.argv) > 1:
        # User provided a file path
        audio_files = [os.path.expanduser(sys.argv[1])]
    else:
        # Try to search for files automatically
        print("\nAttempting to search for audio files automatically...")
        
        # Use filename keywords mentioned by user for search
        search_keywords = [
            'Lojong2TrainingTheMind', 
            'JetsunKhandroRinpoche',
            'Lojong'
        ]
        
        audio_files = []
        for keyword in search_keywords:
            found_files = find_file_in_downloads(keyword)
            audio_files.extend(found_files)
        
        # Deduplicate
        audio_files = list(set(audio_files))
        
        # Filter out non-audio files
        audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
        audio_files = [f for f in audio_files if any(f.lower().endswith(ext) for ext in audio_extensions)]
        
        if not audio_files:
            print("❌ No matching audio files found.")
            print("Please try providing the file path directly:")
            print("python process_audio.py /path/to/your/audio/file.m4a")
            return
        
        if len(audio_files) == 1:
            print(f"✅ Found one matching file: {audio_files[0]}")
        else:
            print(f"✅ Found multiple matching files ({len(audio_files)}):")
            for i, file_path in enumerate(audio_files, 1):
                print(f"{i}. {file_path}")
            
            try:
                choice = int(input("Please select the file number to process (1-{}): ".format(len(audio_files))))
                if 1 <= choice <= len(audio_files):
                    audio_files = [audio_files[choice-1]]
                else:
                    print("❌ Invalid selection, will process the first file")
                    audio_files = [audio_files[0]]
            except ValueError:
                print("❌ Invalid input, will process the first file")
                audio_files = [audio_files[0]]
    
    for audio_file in audio_files:
        print(f"\nTarget file: {audio_file}")
        
        # Check if file exists
        if not os.path.exists(audio_file):
            print(f"❌ Error: File '{audio_file}' does not exist.")
            continue
        
        try:
            total_start_time = time.time()
            
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
            
        except KeyboardInterrupt:
            print("\n⚠️ Processing interrupted by user.")
        except Exception as e:
            print(f"❌ Processing failed: {str(e)}")
            print("Please check the error message and try to resolve the issue.")

if __name__ == "__main__":
    main()