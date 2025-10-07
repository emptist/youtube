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

# Function to check if ffmpeg is installed
check_ffmpeg() {
    if ! command -v ffmpeg &> /dev/null; then
        echo -e "\nWarning: ffmpeg is not detected!"
        echo "Some audio formats may not be supported."
        echo "Installation instructions:"
        echo "- macOS: brew install ffmpeg"
        echo "- Windows: Download from https://ffmpeg.org/download.html"
        echo "- Linux: Use your package manager (e.g., sudo apt install ffmpeg)"
        echo -e "\nPress Enter to continue..."
        read -r
    fi
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