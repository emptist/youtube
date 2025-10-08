# SwiftUI YouTube Downloader with PythonKit Integration

This is a SwiftUI application that uses PythonKit to leverage Python libraries for downloading YouTube videos and processing audio files.

## Requirements

1. macOS 13.0+ (Ventura) or newer
2. Xcode 14.0+ with Swift 5.8+
3. Python 3.8+ installed on your system
4. Python libraries:
   - yt-dlp
   - librosa
   - noisereduce
   - numpy
   - ffmpeg (command-line tool)

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install yt-dlp librosa noisereduce numpy
```

### 2. Install FFmpeg

FFmpeg is required for audio extraction and processing:

```bash
# Using Homebrew
brew install ffmpeg
```

### 3. Clone the Repository

```bash
git clone <repository-url>
cd youtube/swiftui_app
```

### 4. Build and Run the Application

```bash
# Build the application
swift build

# Run the application
swift run
```

Alternatively, you can open the project in Xcode and run it from there:

```bash
open Package.swift
```

## How to Use

1. Enter a valid YouTube URL in the text field
2. Toggle the "Keep original audio file" option if you want to preserve the original downloaded audio
3. Click the "Download and Process" button
4. The application will:
   - Download the audio from the YouTube video
   - Process the audio to reduce noise
   - Save the processed audio file in the `downloads` directory

## Project Structure

```
swiftui_app/
├── Package.swift         # SPM package configuration
├── README.md             # This documentation
├── Sources/
│   └── SwiftUIDownloader/
│       └── SwiftUIDownloader.swift  # Main application code
└── downloads/            # Directory where downloaded files are stored
```

## Troubleshooting

### Python Path Issues

If the application can't find your Python installation, you may need to set the PYTHONPATH environment variable:

```bash
export PYTHONPATH="/usr/local/lib/python3.8/site-packages"  # Adjust to your Python version
```

### Missing Dependencies

Ensure all required Python libraries and FFmpeg are installed correctly.

### Xcode Compatibility

If you encounter issues building in Xcode, make sure you're using the latest version of Xcode and have selected the correct development team.

## Notes

- This application is designed for macOS only at this time
- The noise reduction quality may vary depending on the input audio
- Large audio files may take longer to process

## License

[MIT](LICENSE)