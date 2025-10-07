# YouTube Media Downloader

A simple set of scripts to download audio and video from YouTube using yt-dlp.

## Features

- Download audio in M4A format
- Download video in MP4 format
- Configurable download directory (defaults to ~/Download)
- SSL configuration to handle certificate issues
- Proxy support
- Retry mechanism for improved stability

## Requirements

### Using pip

```bash
pip install -r requirements.txt
```

The requirements.txt includes:
- yt-dlp: Core package for YouTube downloading
- noisereduce: For audio noise reduction
- librosa and soundfile: Dependencies for noisereduce

### Using pixi

If you have pixi installed, you can create a pixi.toml file with:

```toml
[project]
name = "youtube-media-downloader"
version = "0.1.0"
description = "Download audio and video from YouTube"

[dependencies]
yt-dlp = ">=2024.0"
noisereduce = ">=2.0"
librosa = ">=0.10.0"
soundfile = ">=0.12.0"
```

Then install with:

```bash
pixi install
```

### Other Package Management Approaches

#### Using conda

```bash
conda create -n youtube-downloader python=3.11
conda activate youtube-downloader
pip install -r requirements.txt
```

#### Using virtualenv

```bash
virtualenv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

## Usage

### Download Audio

```bash
python extract_audio.py
```

### Download Video

```bash
python download_video.py
```

## Configuration

You can modify the following in both scripts:

- `URLS`: The YouTube URLs to download
- `download_dir`: The directory where files will be saved
- `proxy`: Proxy settings
- `retries` and `socket_timeout`: Download stability settings

## Notes

- **ffmpeg is required** for all functionality, including MP3 compression and audio format conversion.
- Installation instructions for ffmpeg are provided below.
- For macOS users: Install ffmpeg using Homebrew with `brew install ffmpeg`
- For Windows users: Download ffmpeg from https://ffmpeg.org/download.html and add it to your system PATH

## Simple YouTube Downloader (GUI App)

A user-friendly Tkinter-based graphical interface for downloading YouTube audio or video content without complex processing.

### Features
- Clean and intuitive user interface
- Paste YouTube URLs directly from clipboard
- Choose download directory
- Select download type (Audio Only or Video with Audio)
- For audio downloads: choose format (M4A for high quality or MP3 for compatibility)
- For video downloads: get best available quality in MP4 format
- Real-time download progress display
- Status updates throughout the download process
- ffmpeg detection and compatibility handling
- System proxy detection with automatic selection when available
- Configurable proxy settings (system proxy or custom proxy URL)

### Usage
1. Ensure all required dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python simple_downloader.py
   ```
   Or (if executable permissions are set):
   ```bash
   ./simple_downloader.py
   ```
3. Enter or paste a YouTube URL in the input field
4. Choose your preferred download directory
5. Select your download type:
   - "Audio Only" for audio files
   - "Video with Audio (Single File)" for combined video and audio in one file
6. If selecting audio, choose your preferred format (M4A or MP3)
7. Configure proxy settings if needed:
   - System proxy will be automatically detected and selected if available
   - Check "Use Custom Proxy" and enter a proxy URL for custom configuration
8. Click "Download" to start the process
9. Monitor progress in the status window and progress bar

### Notes
- Tkinter is required but typically comes pre-installed with Python
- For best MP3 conversion results, ensure ffmpeg is installed on your system
- The application automatically detects system proxy settings on startup and selects them by default
- When using video download, a single file containing both video and audio will be saved in MP4 format
- Video files may be large, ensure you have sufficient disk space before downloading
- Proxy settings can be toggled on/off as needed for different network environments

## New Integrated Tools

### download_process_audio.py

An all-in-one tool that combines downloading, raw audio saving, noise reduction, and denoised audio saving into a single workflow.

**Key Features:**
- 4-step integrated process: YouTube audio download → Save raw audio → Apply noise reduction → Save denoised audio
- No need for ffmpeg when working with M4A files (uses WAV-to-MP3 workaround)
- Progress bars for each processing stage
- Chunk-based processing for efficient handling of large files
- Error handling for robust operation

**Usage:**

```bash
python download_process_audio.py "YOUTUBE_URL"
```

**Important Note for URL Quoting:**
When using URLs with special characters (like '&' or '=') in shells like zsh, you must enclose the URL in quotes:

```bash
# Correct usage with quotes
python download_process_audio.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### process_simple.py

A streamlined version of the audio processing workflow, focusing on simplicity and ease of use.

**Usage:**

```bash
python process_simple.py
```

### test_integration.py

A testing utility to verify the integrated workflow without requiring actual YouTube downloads. Useful for development and debugging.

**Usage:**

```bash
python test_integration.py
```

## M4A File Handling Update

Recent updates to the codebase have improved M4A file handling by implementing a workaround that:
- Eliminates the dependency on ffmpeg for saving M4A files
- Uses a WAV-to-MP3 conversion method that works with the installed audio libraries
- Maintains audio quality while ensuring compatibility across different systems

This change has been applied to all relevant scripts, including de_noise.py, extract_and_save.py, and test_saving.py. The integrated download_process_audio.py tool also incorporates this improved handling method.

## Audio Noise Reduction

This project also includes tools to reduce noise in audio files with advanced features for handling large files:

### de_noise.py

A general-purpose script for reducing noise in audio files. It uses the noisereduce library to automatically detect and reduce background noise.

**Key Features:**
- Progress bar with processing feedback
- Automatic timing for each processing stage
- File size detection with large file warnings
- Chunk-based processing for efficient handling of large files
- Error handling and detailed status messages

**Usage:**

```bash
python de_noise.py /path/to/your/audio/file.m4a
```

**Options:**
- `-o, --output`: Specify output file path
- `-d, --duration`: Duration of noise sample to use (in seconds), default is 2.0 seconds
- `-c, --chunk`: Chunk duration for processing (in seconds), default is 30 seconds

### test_noise_reduction.py

A convenience script specifically designed to process the audio file mentioned by the user:
`Lojong2TrainingTheMind-JetsunKhandroRinpoche2⧸2.m4a`

**Key Features:**
- User-friendly interface with clear instructions
- Total processing time calculation
- Keyboard interrupt handling (Ctrl+C to stop)
- Detailed error messages
- Helpful post-processing tips

**Usage:**

```bash
python test_noise_reduction.py
```

This script will automatically attempt to process the file in your ~/Download folder and save the result with '_denoised' suffix.

### Performance Considerations

- For large audio files (100MB+), processing time will be longer
- The chunk-based processing helps manage memory usage with large files
- You can adjust the chunk duration parameter based on your system's capabilities
- Processing time depends on your CPU performance and the file size

### Example Output

```
=== Audio Noise Reduction Tool ===
This script will process the specified audio file to reduce background noise

Preparing for processing...
Target file: /Users/username/Downloads/Lojong2TrainingTheMind-JetsunKhandroRinpoche2/2.m4a

Starting file processing...
- Processing progress bar and timing for each stage will be displayed
- Processing may take some time for large files
- Press Ctrl+C to interrupt processing at any time

----------------------------------
Loading audio file: /Users/username/Downloads/Lojong2TrainingTheMind-JetsunKhandroRinpoche2/2.m4a
Audio loaded successfully, sample rate: 44100 Hz, duration: 59.34 seconds
Loading time: 1.23 seconds
File size: 223.54 MB
Note: File is large, processing may take some time.
Applying noise reduction processing...
Processing progress: 100%|██████████| 2/2 [00:15<00:00,  7.52s/it]
Noise reduction processing complete, time taken: 15.32 seconds
Saving processed audio to: /Users/username/Downloads/Lojong2TrainingTheMind-JetsunKhandroRinpoche2/2_denoised.m4a
Audio saved successfully! Saving time: 2.15 seconds

----------------------------------

✅ Noise reduction processing complete!
Total time: 18.70 seconds
Original file: /Users/username/Downloads/Lojong2TrainingTheMind-JetsunKhandroRinpoche2/2.m4a
Processed file: /Users/username/Downloads/Lojong2TrainingTheMind-JetsunKhandroRinpoche2/2_denoised.m4a
```

## Standalone Denoise Applications

The project includes dedicated standalone applications for audio noise reduction that can be used independently of the YouTube downloader functionality.

### standalone_denoise_app Directory

Located in the `standalone_denoise_app/` folder, these applications provide user-friendly interfaces for processing existing audio files without any YouTube-related features.

### Included Applications

1. **Single-file Denoise App** (`denoise_app.py`) - For processing individual audio files
2. **Batch Denoise App** (`denoise_batch_app.py`) - For processing multiple audio files at once

### Key Features

- Intuitive graphical user interfaces
- Adjustable noise reduction parameters
- Progress tracking during processing
- Detailed logging of operations
- Support for various audio formats (M4A, MP3, WAV, FLAC, OGG, AAC)
- Batch processing capabilities
- File list management (add, remove, clear)
- Output directory customization

### Installation

1. Navigate to the standalone denoise app directory:
   ```bash
   cd standalone_denoise_app
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure ffmpeg is installed (required for format support)

### Usage

The standalone denoise applications can be started in several ways:

#### Using the Launcher Script
```bash
./launch_denoise_apps.sh
```
This will display a menu allowing you to choose between the single-file and batch applications, or install dependencies.

#### Running Directly
```bash
python3 denoise_app.py       # For single-file processing
python3 denoise_batch_app.py # For batch processing
```

For detailed usage instructions, please refer to the `README.md` file inside the `standalone_denoise_app` directory.

### Ideal Use Cases

These standalone applications are perfect for:
- Processing collections of existing audio files
- Denoising voice recordings, podcasts, or music files
- Batch processing large numbers of files
- Users who only need noise reduction functionality without YouTube downloading

For more information about the standalone denoise applications, including detailed usage instructions and troubleshooting tips, please refer to the documentation in the `standalone_denoise_app` directory.