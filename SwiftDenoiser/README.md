# SwiftDenoiser

This is a standalone SwiftUI application that uses PythonKit to leverage Python libraries for audio noise reduction.

## Description

SwiftDenoiser provides a simple user interface for selecting audio files, specifying output locations, and applying noise reduction to your audio recordings. It integrates with Python libraries to perform high-quality audio processing.

## Requirements

1. macOS 13.0+ (Ventura) or newer
2. Xcode 14.0+ with Swift 5.8+
3. Python 3.8+ installed on your system
4. Python libraries:
   - librosa
   - noisereduce
   - numpy
   - ffmpeg (command-line tool)

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install librosa noisereduce numpy
```

### 2. Install FFmpeg

FFmpeg is required for audio processing:

```bash
# Using Homebrew
brew install ffmpeg
```

### 3. Clone the Repository

```bash
git clone <repository-url>
cd SwiftDenoiser
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

1. Click the "Select File" button to choose an audio file for processing
2. Click the "Select Output Folder" button to choose where the denoised file will be saved
3. Click the "Denoise" button to start the noise reduction process
4. The application will:
   - Process the selected audio file
   - Apply noise reduction using the Python backend
   - Save the denoised audio file in the specified output folder with "denoised_" prefix

## Project Structure

```
SwiftDenoiser/
├── Package.swift         # SPM package configuration
├── README.md             # This documentation
└── Sources/
    └── SwiftDenoiser/
        └── SwiftDenoiser.swift  # Main application code
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

If you encounter issues building in Xcode, make sure you're using the latest version of Xcode.

## Notes

- This application is designed for macOS only at this time
- The noise reduction quality may vary depending on the input audio characteristics
- Supported audio formats depend on what your Python installation can handle
- Large audio files may take longer to process

## License

[MIT](LICENSE)