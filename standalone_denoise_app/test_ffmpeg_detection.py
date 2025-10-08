#!/usr/bin/env python3
import os
import subprocess

"""
Test script to verify ffmpeg detection
This script uses the same detection methods implemented in the denoise apps
"""

print("=== FFmpeg Detection Test ===\n")

# Method 1: which/where command
print("Method 1: Checking PATH via command...")
if os.name == 'posix':  # macOS/Linux
    result = os.system('which ffmpeg > /dev/null 2>&1')
    if result == 0:
        print("✓ Success: ffmpeg found in PATH using 'which' command")
        # Show the actual path
        path = subprocess.check_output(['which', 'ffmpeg']).decode('utf-8').strip()
        print(f"  Path: {path}")
    else:
        print("✗ Failed: 'which' command couldn't find ffmpeg in PATH")
elif os.name == 'nt':  # Windows
    result = os.system('where ffmpeg > NUL 2>&1')
    if result == 0:
        print("✓ Success: ffmpeg found in PATH using 'where' command")
        # Show the actual path
        path = subprocess.check_output(['where', 'ffmpeg']).decode('utf-8').strip()
        print(f"  Path: {path}")
    else:
        print("✗ Failed: 'where' command couldn't find ffmpeg in PATH")

# Method 2: Direct command execution
print("\nMethod 2: Direct command execution...")
try:
    subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    print("✓ Success: ffmpeg command executed successfully")
except (subprocess.SubprocessError, FileNotFoundError):
    print("✗ Failed: Could not execute ffmpeg command directly")

# Method 3: Check common installation paths
print("\nMethod 3: Checking common installation paths...")
common_paths = []
if os.name == 'posix':
    common_paths = ['/usr/local/bin/ffmpeg', '/opt/homebrew/bin/ffmpeg', '/usr/bin/ffmpeg']
elif os.name == 'nt':
    common_paths = [os.path.join(os.environ.get('ProgramFiles', ''), 'ffmpeg', 'bin', 'ffmpeg.exe')]

found_path = None
for path in common_paths:
    if os.path.exists(path) and os.access(path, os.X_OK):
        found_path = path
        break

if found_path:
    print(f"✓ Success: ffmpeg found at common path: {found_path}")
else:
    print("✗ Failed: Could not find ffmpeg in common installation paths")
    print("  Checked paths:")
    for path in common_paths:
        print(f"  - {path}")

# Final summary
print("\n=== Summary ===")
# Try to run ffmpeg version to get full info
if os.name == 'posix':
    try:
        version_output = subprocess.check_output(['ffmpeg', '-version'], stderr=subprocess.STDOUT).decode('utf-8')
        print("ffmpeg is installed and working!")
        # Print just the first line which contains version info
        print(version_output.split('\n')[0])
    except:
        print("ffmpeg is not properly installed or not accessible.")
        print("\nInstallation instructions:")
        print("- macOS: brew install ffmpeg")
        print("- Windows: Download from https://ffmpeg.org/download.html")
        print("- Linux: Use your package manager (e.g., sudo apt install ffmpeg)")

print("\nNote: The denoise apps have been updated with improved ffmpeg detection logic.")
print("If you're still having issues, make sure ffmpeg is in your system PATH or installed in one of the common locations.")