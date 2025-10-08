# Simple YouTube Downloader (Standalone App)

This directory contains the standalone version of the Simple YouTube Downloader application.

## What's Included

- `simple_downloader.py`: The original source code
- `requirements.txt`: Minimal dependencies (yt-dlp)
- `venv/`: Python virtual environment with PyInstaller and dependencies
- `dist/`: Contains the built standalone application (SimpleYouTubeDownloader.app on macOS)

## How to Use the Standalone Application

### macOS

1. Navigate to the `dist` folder
2. Double-click on `SimpleYouTubeDownloader.app` to run the application

### Notes

- The application is self-contained and doesn't require Python to be installed
- **ffmpeg is required** for all functionality, including MP3 conversion
- On macOS, you may need to right-click and select "Open" the first time you run the application to bypass Gatekeeper
- For macOS users: Install ffmpeg using Homebrew with `brew install ffmpeg`
- For Windows users: Download ffmpeg from https://ffmpeg.org/download.html and add it to your system PATH

## Rebuilding the Application

If you need to rebuild the application after making changes to the source code:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run PyInstaller again
pyinstaller --onefile --windowed --name SimpleYouTubeDownloader simple_downloader.py
```

The updated application will be created in the `dist` folder.

## Troubleshooting

- If the application fails to run, make sure you have the latest version of yt-dlp in the requirements.txt
- For issues with downloading videos, check your internet connection and proxy settings
- If you encounter issues with MP3 conversion, verify that ffmpeg is properly installed on your system