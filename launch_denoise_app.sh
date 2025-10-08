#!/bin/bash

# Function to check if ffmpeg is installed with improved detection
check_ffmpeg() {
    # Method 1: command -v (standard way)
    if command -v ffmpeg >/dev/null 2>&1; then
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
    echo "Installation instructions for different platforms:" >&2
    echo "- macOS: brew install ffmpeg" >&2
    echo "- Ubuntu/Debian: sudo apt install ffmpeg" >&2
    echo "- Windows: Download from https://ffmpeg.org/download.html" >&2
    
    echo -e "\nPress Enter to exit..."
    read -r
    return 1
}

# Check for ffmpeg
echo -e "\nChecking for ffmpeg installation..."
check_ffmpeg

# Run the application
echo -e "\nStarting Denoise App...\n"
python3 denoise_app.py
exit_code=$?
echo "Application exited with code $exit_code"
read -p "Press Enter to continue..."
