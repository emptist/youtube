# SwiftDenoiserXcode

SwiftDenoiserXcode is a SwiftUI-based macOS application for reducing noise in audio files. It provides a native macOS interface for audio noise reduction with advanced configuration options.

## Features

- Native SwiftUI interface for macOS
- Process individual audio files
- Adjustable noise reduction parameters
- Progress bar for tracking processing
- Detailed logging with timestamps
- Support for various audio formats
- ffmpeg installation detection
- Cancel functionality during processing

## Requirements

- macOS 13.0 (Ventura) or later
- Swift 5.8 or later
- Xcode 14.3 or later
- Python (for noise reduction functionality)
- ffmpeg (required for audio format conversion)

## Installation

### Using Swift Package Manager

1. Clone or download this repository
2. Navigate to the SwiftDenoiserXcode directory
3. Run the application with:
   
   ```bash
   swift run SwiftDenoiserXcode
   ```

### Using Xcode

1. Open the SwiftDenoiserXcode directory in Xcode
2. Build and run the application (⌘R)

## Usage

1. Launch the SwiftDenoiserXcode application
2. Click "Browse" to select an input audio file
3. Click "Browse" to select an output file location
4. Adjust the noise reduction settings as needed:
   - **Noise Sample Duration**: Length of the initial silence used for noise profile (0.5-10 seconds)
   - **Processing Chunk Duration**: Size of chunks used for processing large files (10-300 seconds)
   - Check "Keep original file" if you don't want to overwrite the original
5. Click "Apply Noise Reduction" to start processing
6. Monitor progress in the status window and progress bar
7. Use the "Cancel" button if you need to stop processing

## Python Dependencies

The noise reduction functionality relies on the following Python packages:

```bash
pip install noisereduce librosa soundfile numpy tqdm
```

## ffmpeg Installation

ffmpeg is required for audio format conversion. You can install it using Homebrew:

```bash
brew install ffmpeg
```

## Technical Details

SwiftDenoiserXcode uses PythonKit to integrate with the Python `de_noise.py` script located in the root directory of the repository. This script performs the actual noise reduction using specialized audio processing libraries.

## Project Structure

```
SwiftDenoiserXcode/
├── .gitignore               # Git ignore file
├── Package.swift            # Swift Package Manager configuration
├── Package.resolved         # Resolved package dependencies
└── Sources/
    └── SwiftDenoiserXcode/
        └── SwiftDenoiserXcode.swift # Main application code
```

## License

This project is licensed under the MIT License.

## Building for Distribution

To create a standalone macOS application bundle (.app) for distribution, follow these steps:

### Using Xcode

1. Open the SwiftDenoiserXcode directory in Xcode
2. Select "Product" > "Archive" from the menu bar
3. Once the archive is complete, the Organizer window will open
4. Select the archive and click "Distribute App"
5. Choose "Copy App" and click "Next"
6. Select a destination folder and click "Export"
7. You'll get a `SwiftDenoiserXcode.app` file that can be distributed

### Using Command Line

1. Open Terminal and navigate to the SwiftDenoiserXcode directory
2. Run the following command to build a release version:
   
   ```bash
   swift build -c release --arch arm64 --arch x86_64
   ```
   This creates a universal binary supporting both Intel and Apple Silicon Macs
3. The built executable will be located at:
   
   ```
   .build/apple/Products/Release/SwiftDenoiserXcode
   ```
4. To create a proper .app bundle, you'll need to create the necessary directory structure:
   
   ```bash
   mkdir -p SwiftDenoiserXcode.app/Contents/MacOS
   mkdir -p SwiftDenoiserXcode.app/Contents/Resources
   ```
5. Copy the executable into the MacOS directory:
   
   ```bash
   cp .build/apple/Products/Release/SwiftDenoiserXcode SwiftDenoiserXcode.app/Contents/MacOS/
   ```
6. Create a basic Info.plist file in the Contents directory:
   
   ```bash
   cat > SwiftDenoiserXcode.app/Contents/Info.plist << EOF
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>CFBundleExecutable</key>
       <string>SwiftDenoiserXcode</string>
       <key>CFBundleIdentifier</key>
       <string>com.yourdomain.SwiftDenoiserXcode</string>
       <key>CFBundleInfoDictionaryVersion</key>
       <string>6.0</string>
       <key>CFBundleName</key>
       <string>SwiftDenoiserXcode</string>
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