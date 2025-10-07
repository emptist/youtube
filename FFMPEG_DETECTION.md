# FFMPEG Detection and Format Option Handling in Simple YouTube Downloader

## Overview
This document explains how the Simple YouTube Downloader application handles FFMPEG detection and manages format options based on FFMPEG availability.

## FFMPEG Detection Implementation

### Initialization Process
The application follows a specific initialization order to properly handle FFMPEG detection and GUI component creation:

1. **Initialize FFMPEG status flag** - Set `self.has_ffmpeg = False` before creating GUI components
   ```python
   # Initialize ffmpeg status to False before GUI creation
   self.has_ffmpeg = False
   ```

2. **Create GUI components** - Build all UI elements including the status text widget needed for logging
   ```python
   # Create GUI components
   self.create_widgets()
   ```

3. **Check FFMPEG installation** - Perform the actual FFMPEG detection after the GUI is fully initialized
   ```python
   # Now check for ffmpeg installation after GUI is ready
   self.check_ffmpeg_installation()
   ```

### Detection Mechanism
The `check_ffmpeg_installation()` method uses the `subprocess` module to determine if FFMPEG is available in the system PATH:

```python
def check_ffmpeg_installation(self):
    try:
        # Try to find ffmpeg in PATH
        if subprocess.run(['which', 'ffmpeg'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
            self.has_ffmpeg = True
            self.log_message("ffmpeg installation detected. Better audio processing available.")
        else:
            self.has_ffmpeg = False
            self.log_message("Note: ffmpeg not detected. Some advanced features may be limited.")
    except Exception:
        self.has_ffmpeg = False
        self.log_message("Error checking ffmpeg installation status")
```

## Format Option Handling

### Dynamic UI Management
The application dynamically manages the visibility of the MP3 format option based on both the selected download type and FFMPEG availability:

```python
def toggle_format_options(self):
    """Toggle format options based on download type selection and ffmpeg availability"""
    if self.download_type.get() == "audio":
        self.m4a_radio.config(state=tk.NORMAL)
        # Show MP3 option only if ffmpeg is available
        if self.has_ffmpeg:
            self.mp3_radio.pack(side=tk.LEFT, padx=10)  # Make MP3 option visible
            self.mp3_radio.config(state=tk.NORMAL)
        else:
            self.mp3_radio.pack_forget()  # Hide MP3 option
            self.format_var.set("m4a")  # Ensure M4A is selected
        self.format_frame.config(text="Audio Format Options")
    else:
        # For video downloads, hide audio format options
        self.m4a_radio.config(state=tk.DISABLED)
        self.mp3_radio.pack_forget()  # Hide MP3 option
        self.format_frame.config(text="Video will be downloaded in MP4 format")
```

### Key Features
- **Clean UI experience** - The MP3 option is completely hidden (not just disabled) when FFMPEG is not available
- **Automatic default selection** - M4A format is automatically selected when MP3 is not available
- **Contextual UI updates** - The format frame text updates based on the selected download type
- **Error prevention** - Users can't select incompatible formats when FFMPEG is not installed, preventing potential download errors

## Technical Considerations

### Why This Implementation?
- **Circular dependency prevention** - By initializing `self.has_ffmpeg` before GUI creation but performing the actual check after, we avoid AttributeError issues
- **User experience** - Hiding unavailable options provides a cleaner interface than showing disabled options
- **Error prevention** - Automatically selecting a compatible format reduces user confusion and potential errors
- **Performance** - The FFMPEG check is performed only once during initialization, minimizing system resource usage

## Troubleshooting
If users experience issues with format options or FFMPEG detection:
- Ensure FFMPEG is properly installed and added to the system PATH
- Check the application logs for messages about FFMPEG detection status
- Verify that the desired format is compatible with the selected download type