#!/bin/bash

# This script provides a simple launcher for the standalone denoise applications

# Change to the script's directory
dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$dir"

# Function to display the menu
show_menu() {
    clear
    echo "====================================="
    echo "    Audio Noise Reduction Tools     "
    echo "====================================="
    echo "1. Single File Denoise Application  "
    echo "2. Batch File Denoise Application   "
    echo "3. Install Dependencies             "
    echo "4. Exit                             "
    echo "====================================="
    echo -n "Enter your choice [1-4]: "
}

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
    echo "Installation instructions for different platforms:" >&2
    echo "- macOS: brew install ffmpeg" >&2
    echo "- Ubuntu/Debian: sudo apt install ffmpeg" >&2
    echo "- Windows: Download from https://ffmpeg.org/download.html" >&2
    
    # Offer to help test ffmpeg detection
    echo "\nYou can run the test script to diagnose ffmpeg detection issues:" >&2
    echo "python test_ffmpeg_detection.py" >&2
    
    echo -e "\nPress Enter to continue..."
    read -r
    return 1
}

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "Dependencies installed successfully!"
    else
        echo "Failed to install dependencies. Please try again with administrative privileges."
    fi
    echo "Press Enter to continue..."
    read -r
}

# Main loop
while true; do
    show_menu
    read -r choice
    case $choice in
        1)  check_ffmpeg
            echo "Starting Single File Denoise Application..."
            python3 denoise_app.py
            echo "Application exited. Press Enter to return to menu..."
            read -r
            ;;
        2)  check_ffmpeg
            echo "Starting Batch File Denoise Application..."
            python3 denoise_batch_app.py
            echo "Application exited. Press Enter to return to menu..."
            read -r
            ;;
        3)  install_dependencies
            ;;
        4)  echo "Thank you for using Audio Noise Reduction Tools!"
            exit 0
            ;;
        *)  echo "Invalid choice. Please enter a number between 1 and 4."
            echo "Press Enter to continue..."
            read -r
            ;;
    esac
done