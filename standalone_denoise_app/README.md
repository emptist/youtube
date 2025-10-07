# Standalone Audio Noise Reduction Applications

This directory contains self-contained audio noise reduction applications that can be run independently without any YouTube downloader functionality.

## Included Applications

1. **Single-file Denoise App** (`denoise_app.py`) - For processing individual audio files
2. **Batch Denoise App** (`denoise_batch_app.py`) - For processing multiple audio files at once

## Features

### Common Features
- Intuitive graphical user interface
- Adjustable noise reduction parameters
- Progress tracking during processing
- Detailed logging of operations
- Support for various audio formats (M4A, MP3, WAV, FLAC, OGG, AAC)
- Automatic ffmpeg detection

### Batch Denoise App Additional Features
- Multi-file selection and processing
- File list management (add, remove, clear)
- Output directory customization
- Batch progress tracking
- Summary report of successful/failed processing
- Error handling for each file in batch

## Installation

1. Ensure you have Python 3 installed on your system
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make sure ffmpeg is installed (required for format support):
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
   - **Linux**: Use your package manager (e.g., `sudo apt install ffmpeg`)

## Usage

### Running the Applications

#### From the Command Line
Navigate to this directory and run:
```
python3 denoise_app.py       # For single-file processing
python3 denoise_batch_app.py # For batch processing
```

#### Making the Applications Executable
You can make the applications directly executable by running:
```
chmod +x denoise_app.py denoise_batch_app.py
```
Then you can run them with:
```
./denoise_app.py
./denoise_batch_app.py
```

### Single-file Denoise App Instructions
1. Click the "Browse" button to select an input audio file
2. The output file path will be automatically suggested (original filename with "_denoised" suffix)
3. Optionally, adjust the noise reduction parameters:
   - **Noise Sample Duration**: Length of the initial silence used for noise profile
   - **Processing Chunk Duration**: Size of chunks used for processing large files
4. Check "Keep original file" if you don't want to overwrite the original
5. Click "Apply Noise Reduction" to start processing
6. Monitor progress in the status window

### Batch Denoise App Instructions
1. Click "Add Files" to select multiple audio files for processing
2. Use "Remove Selected" or "Clear All" to manage your file list
3. Select an output directory where denoised files will be saved
4. Adjust noise reduction parameters as needed
5. Click "Apply Noise Reduction to All" to start batch processing
6. Monitor overall progress and individual file status
7. After completion, review the summary report

## Noise Reduction Parameters

- **Noise Sample Duration**: Typically 1-5 seconds of background noise at the beginning of the audio
- **Processing Chunk Duration**: Smaller values (10-30s) use less memory but may take longer
- Larger values (60-300s) process faster but require more memory

## Notes
- For best results, ensure your audio files have a few seconds of consistent background noise at the beginning
- Processing time depends on file size, your computer's performance, and the selected chunk duration
- The applications run processing in a separate thread, so the GUI remains responsive during operations
- If you encounter format-related issues, make sure ffmpeg is properly installed

## Error Handling
- The applications will display informative error messages if processing fails
- In batch mode, a single file failure won't stop the entire batch processing
- Check the status log for detailed information about any errors

## Creating a Portable Version

To create a truly portable version that doesn't require Python installation, you can use tools like PyInstaller:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Create a standalone executable for either application:
   ```
   pyinstaller --onefile --windowed denoise_app.py
   pyinstaller --onefile --windowed denoise_batch_app.py
   ```

3. The executable files will be created in the `dist` directory

## Troubleshooting

**Common Issues and Solutions:**

1. **ffmpeg not detected**: Install ffmpeg using your system's package manager or download it from https://ffmpeg.org

2. **Memory errors with large files**: Reduce the chunk duration parameter

3. **Files not processing**: Check that you have write permissions to the output directory

4. **Format conversion issues**: Ensure ffmpeg is properly installed for comprehensive format support

5. **Dependency errors**: Make sure all dependencies from requirements.txt are properly installed