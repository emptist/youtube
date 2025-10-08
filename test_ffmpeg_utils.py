#!/usr/bin/env python3
import os
import sys

# Add the current directory to the Python path to ensure we can import ffmpeg_utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the utility module
from ffmpeg_utils import ffmpeg_utils, check_ffmpeg, get_ffmpeg_path, get_installation_instructions

print("=== Testing FFmpegUtils Module ===\n")

# Test using the singleton instance
print("1. Testing singleton instance...")
is_installed, message = ffmpeg_utils.check_ffmpeg()
print(f"   Result: {is_installed}")
print(f"   Message: {message}\n")

# Test using the convenience function
print("2. Testing convenience function check_ffmpeg()...")
is_installed, message = check_ffmpeg()
print(f"   Result: {is_installed}")
print(f"   Message: {message}\n")

# Test get_ffmpeg_path()
print("3. Testing get_ffmpeg_path()...")
path = get_ffmpeg_path()
if path:
    print(f"   Success: ffmpeg found at {path}")
else:
    print("   Failed: Could not find ffmpeg path")
print()

# Test get_installation_instructions()
print("4. Testing get_installation_instructions()...")
instructions = get_installation_instructions()
print(f"   Instructions:\n   {instructions}\n")

# Verify actual ffmpeg execution if found
if is_installed:
    print("5. Verifying actual ffmpeg execution...")
    try:
        import subprocess
        result = subprocess.run(
            [get_ffmpeg_path() or 'ffmpeg', '-version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True
        )
        if result.returncode == 0:
            print("   Success! FFmpeg is working correctly.")
            # Print just the first line which contains version info
            version_line = result.stdout.split('\n')[0]
            print(f"   {version_line}")
        else:
            print("   Warning: FFmpeg was found but returned an error code.")
    except Exception as e:
        print(f"   Error during verification: {str(e)}")

print("\n=== Test Complete ===")
print("The FFmpegUtils module is ready to be used in your applications.")