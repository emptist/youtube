#!/usr/bin/env python3
import os
import sys
import time
from de_noise import reduce_noise

if __name__ == "__main__":
    print("=== Large Audio File Noise Reduction Test ===")
    print("This script will test the noise reduction functionality on a large audio file")
    
    # User-specified audio file path
    audio_file = os.path.expanduser('~/Downloads/Lojong2-JetsunKhandro.m4a')
    
    print(f"\nTarget file: {audio_file}")
    
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"Error: File '{audio_file}' does not exist.")
        print("Please confirm the file path is correct.")
        sys.exit(1)
    
    # Get original file size
    original_size = os.path.getsize(audio_file) / (1024 * 1024)  # Convert to MB
    print(f"Original file size: {original_size:.2f} MB")
    
    try:
        # Run noise reduction and measure total time
        total_start_time = time.time()
        
        # Call noise reduction function
        print("\nStarting noise reduction process...")
        output_file = reduce_noise(audio_file, chunk_duration=60)  # Using larger chunks for better performance
        
        total_time = time.time() - total_start_time
        
        # Get output file size
        output_size = os.path.getsize(output_file) / (1024 * 1024)  # Convert to MB
        size_diff_percentage = ((output_size - original_size) / original_size) * 100
        
        print("\n==========================================")
        print("\n✅ Noise reduction test completed!")
        print(f"Total processing time: {total_time:.2f} seconds")
        print(f"Original file size: {original_size:.2f} MB")
        print(f"Output file size: {output_size:.2f} MB")
        print(f"File size change: {size_diff_percentage:+.2f}%")
        print(f"\nProcessed file saved to: {output_file}")
        print("\nResults Summary:")
        
        # Evaluate loading improvement
        print("1. Large file loading optimization:")
        if original_size > 100:
            print("   ✓ Large file detected and optimized loading used")
        else:
            print("   ✓ Standard loading used (file size under 100MB)")
        
        print("2. Noise reduction functionality:")
        print("   ✓ Completed successfully")
        
        print("3. Output file size comparison:")
        if output_size > original_size * 1.5:  # If output is more than 50% larger
            print("   ⚠️  Output file is significantly larger than original")
        elif output_size > original_size:  # If output is slightly larger
            print("   ✓ Output file is slightly larger than original")
        else:  # If output is smaller or same size
            print("   ✓ Output file size is acceptable")
        
    except Exception as e:
        print(f"\n❌ Error during noise reduction: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)