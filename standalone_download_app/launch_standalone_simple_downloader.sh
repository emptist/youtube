#!/bin/bash

# Function to check if ffmpeg is installed with improved detection
check_ffmpeg() {
    # Method 1: command -v (standard way)
    if command -v ffmpeg &> /dev/null; then
        echo "✓ ffmpeg found in PATH"
        return 0
    fi
    
    # Method 2: Check common installation paths
    local common_paths=("/usr/local/bin/ffmpeg" "/opt/homebrew/bin/ffmpeg" "/usr/bin/ffmpeg")
    
    for path in "${common_paths[@]}"; do
        if [[ -x "$path" ]]; then
            echo "✓ ffmpeg found at $path"
            # Add to PATH for this session if not already there
            if [[ ! "$PATH" == *"$(dirname "$path")"* ]]; then
                echo "Adding $path to PATH for this session"
                export PATH="$(dirname "$path"):$PATH"
            fi
            return 0
        fi
    done
    
    # If we get here, ffmpeg is not found
    echo "Error: ffmpeg is required but not installed or not in PATH." >&2
    echo "Please install ffmpeg before running this application." >&2
    echo "Installation instructions for different platforms:"
    echo "- macOS: brew install ffmpeg"
    echo "- Ubuntu/Debian: sudo apt install ffmpeg"
    echo "- Windows: Download from https://ffmpeg.org/download.html"
    
    # Offer to help test ffmpeg detection
    echo "\nYou can run the test script to diagnose ffmpeg detection issues:"
    echo "python test_ffmpeg_detection.py"
    
    echo -e "\nPress Enter to continue anyway..."
    read -r
    return 1
}

# Get the directory where this script is located
dir="$( cd "$( dirname "${BASH_SOURCE[0]}")" && pwd )"

# Navigate to the script directory
echo "Changing to script directory: $dir"
cd "$dir"

# Check for ffmpeg
echo -e "\nChecking for ffmpeg installation..."
check_ffmpeg

# Run the application
if [ -f "simple_downloader.py" ]; then
    echo -e "\nStarting Simple YouTube Downloader...\n"
    python3 "simple_downloader.py"
    exit_code=$?
    echo -e "\nApplication exited with code $exit_code"
else
    echo "Error: simple_downloader.py not found in $dir"
    exit_code=1
fi

# Wait for user input before exiting
read -p "Press Enter to continue..."
exit $exit_code
