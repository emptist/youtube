# SwiftYTXcode

SwiftYTXcode is a SwiftUI-based macOS application for downloading audio and video content from YouTube. It provides a clean, native macOS interface for YouTube media downloads with customizable options.

## Features

- Native SwiftUI interface for macOS
- Download YouTube audio in M4A or MP3 format
- Download YouTube video in MP4 format
- Customizable download directory
- Progress tracking during downloads
- Noise reduction option for audio files
- Support for system proxy settings

## Requirements

- macOS 13.0 (Ventura) or later
- Swift 5.8 or later
- Xcode 14.3 or later
- Python (for noise reduction functionality)
- ffmpeg (required for format conversion)

## Installation

### Using Swift Package Manager

1. Clone or download this repository
2. Navigate to the SwiftYTXcode directory
3. Run the application with:
   
   ```bash
   swift run SwiftYTXcode
   ```

### Using Xcode

1. Open the SwiftYTXcode directory in Xcode
2. Build and run the application (⌘R)

## Usage

1. Launch the SwiftYTXcode application
2. Enter or paste a YouTube URL in the input field
3. Choose your preferred download directory by clicking the "Browse" button
4. Select your download type:
   - "Audio Only" for audio files
   - "Video with Audio" for combined video and audio
5. If selecting audio, choose your preferred format (M4A or MP3)
6. Check the "Apply Noise Reduction" option if you want to reduce background noise in audio files
7. Click "Download" to start the process
8. Monitor progress in the status window

## Python Dependencies for Noise Reduction

If you want to use the noise reduction feature, you'll need to install the following Python packages:

```bash
pip install noisereduce librosa soundfile numpy
```

## ffmpeg Installation

ffmpeg is required for format conversion. You can install it using Homebrew:

```bash
brew install ffmpeg
```

## Project Structure

```
SwiftYTXcode/
├── .gitignore               # Git ignore file
├── Package.swift            # Swift Package Manager configuration
├── Package.resolved         # Resolved package dependencies
├── ExampleDownloadOptions.swift # Example implementation of download options UI
└── Sources/
    └── SwiftYTXcode/
        └── SwiftYTXcode.swift # Main application code
```

## License

This project is licensed under the MIT License.

## Building for Distribution

To create a standalone macOS application bundle (.app) for distribution, follow these steps:

### Using Xcode

1. Open the SwiftYTXcode directory in Xcode
2. Select "Product" > "Archive" from the menu bar
3. Once the archive is complete, the Organizer window will open
4. Select the archive and click "Distribute App"
5. Choose "Copy App" and click "Next"
6. Select a destination folder and click "Export"
7. You'll get a `SwiftYTXcode.app` file that can be distributed

### Using Command Line

1. Open Terminal and navigate to the SwiftYTXcode directory
2. Run the following command to build a release version:
   
   ```bash
   swift build -c release --arch arm64 --arch x86_64
   ```
   This creates a universal binary supporting both Intel and Apple Silicon Macs
3. The built executable will be located at:
   
   ```
   .build/apple/Products/Release/SwiftYTXcode
   ```
4. To create a proper .app bundle, you'll need to create the necessary directory structure:
   
   ```bash
   mkdir -p SwiftYTXcode.app/Contents/MacOS
   mkdir -p SwiftYTXcode.app/Contents/Resources
   ```
5. Copy the executable into the MacOS directory:
   
   ```bash
   cp .build/apple/Products/Release/SwiftYTXcode SwiftYTXcode.app/Contents/MacOS/
   ```
6. Create a basic Info.plist file in the Contents directory:
   
   ```bash
   cat > SwiftYTXcode.app/Contents/Info.plist << EOF
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>CFBundleExecutable</key>
       <string>SwiftYTXcode</string>
       <key>CFBundleIdentifier</key>
       <string>com.yourdomain.SwiftYTXcode</string>
       <key>CFBundleInfoDictionaryVersion</key>
       <string>6.0</string>
       <key>CFBundleName</key>
       <string>SwiftYTXcode</string>
       <key>CFBundlePackageType</key>
       <string>APPL</string>
       <key>CFBundleShortVersionString</key>
       <string>1.0</string>
       <key>CFBundleVersion</key>
       <string>1</string>
       <key>LSMinimumSystemVersion</key>
       <string>13.0</string>
       <key>NSHumanReadableCopyright</key>
       <string>Copyright © 2024. All rights reserved.</string>
   </dict>
   </plist>
   EOF
   ```

### Important Notes for Distribution

1. The resulting application bundle will require Python and ffmpeg to be installed on the target machine
2. For a completely self-contained application, you would need to bundle Python and its dependencies, which is beyond the scope of this guide
3. For better user experience, consider creating a disk image (.dmg) for distribution
4. If you plan to distribute the app outside your organization, you should consider code signing and notarization with Apple