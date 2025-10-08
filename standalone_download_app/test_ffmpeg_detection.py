#!/usr/bin/env python3
import os
import subprocess
import shutil

"""
Test script to verify ffmpeg detection for the Simple YouTube Downloader
This script uses the same detection methods implemented in the download app
"""

print("=== FFmpeg Detection Test for Simple YouTube Downloader ===\n")

# Method 1: Direct command execution
print("Method 1: Direct command execution...")
try:
    subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    print("✓ Success: ffmpeg command executed successfully")
except (subprocess.SubprocessError, FileNotFoundError):
    print("✗ Failed: Could not execute ffmpeg command directly")

# Method 2: Check common installation paths based on OS
print("\nMethod 2: Checking common installation paths...")
common_paths = []
if os.name == 'posix':  # macOS/Linux
    common_paths = ['/usr/local/bin/ffmpeg', '/opt/homebrew/bin/ffmpeg', '/usr/bin/ffmpeg', '/bin/ffmpeg']
elif os.name == 'nt':  # Windows
    common_paths = [os.path.join(os.environ.get('ProgramFiles', ''), 'ffmpeg', 'bin', 'ffmpeg.exe')]

found_path = None
for path in common_paths:
    if path and os.path.isfile(path) and os.access(path, os.X_OK):
        found_path = path
        break

if found_path:
    print(f"✓ Success: ffmpeg found at common path: {found_path}")
else:
    print("✗ Failed: Could not find ffmpeg in common installation paths")
    print("  Checked paths:")
    for path in common_paths:
        if path:  # Only print non-empty paths
            print(f"  - {path}")

# Method 3: Use shutil.which to check PATH (more cross-platform)
print("\nMethod 3: Checking PATH using shutil.which...")
ffmpeg_path = shutil.which('ffmpeg')
if ffmpeg_path:
    print(f"✓ Success: ffmpeg found in PATH at: {ffmpeg_path}")
else:
    print("✗ Failed: Could not find ffmpeg in PATH using shutil.which")

# Method 4: System-specific path checking (which/where)
print("\nMethod 4: System-specific PATH checking...")
if os.name == 'posix':  # macOS/Linux
    result = os.system('which ffmpeg > /dev/null 2>&1')
    if result == 0:
        path = subprocess.check_output(['which', 'ffmpeg']).decode('utf-8').strip()
        print(f"✓ Success: ffmpeg found in PATH using 'which' command")
        print(f"  Path: {path}")
    else:
        print("✗ Failed: 'which' command couldn't find ffmpeg in PATH")
elif os.name == 'nt':  # Windows
    result = os.system('where ffmpeg > NUL 2>&1')
    if result == 0:
        path = subprocess.check_output(['where', 'ffmpeg']).decode('utf-8').strip()
        print(f"✓ Success: ffmpeg found in PATH using 'where' command")
        print(f"  Path: {path}")
    else:
        print("✗ Failed: 'where' command couldn't find ffmpeg in PATH")

# Final summary
print("\n=== Summary ===")
# Try to run ffmpeg version to get full info
ffmpeg_installed = False
if os.name == 'posix' or os.name == 'nt':
    try:
        version_output = subprocess.check_output(['ffmpeg', '-version'], stderr=subprocess.STDOUT).decode('utf-8')
        ffmpeg_installed = True
        print("ffmpeg is installed and working!")
        # Print just the first line which contains version info
        print(version_output.split('\n')[0])
    except:
        print("ffmpeg is not properly installed or not accessible.")
        print("\nInstallation instructions:")
        print("- macOS: brew install ffmpeg")
        print("- Windows: Download from https://ffmpeg.org/download.html")
        print("- Linux: Use your package manager (e.g., sudo apt install ffmpeg)")

print("\nNote: The Simple YouTube Downloader has been updated with improved ffmpeg detection logic.")
print("If you're still having issues, make sure ffmpeg is in your system PATH or installed in one of the common locations.")