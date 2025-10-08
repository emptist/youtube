import yt_dlp
import ssl
import os

# Configure SSL context to handle potential certificate issues
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

URLS = [
    'https://www.youtube.com/watch?v=BUJpAzByMjo&t=279s'
]

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Ensure we can import ffmpeg_utils even when running from different locations
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the shared ffmpeg utility
from ffmpeg_utils import check_ffmpeg

# Check if ffmpeg is installed
success, message = check_ffmpeg()
if not success:
    print(f"ERROR: {message}")
    sys.exit(1)

print(message)

# Set download directory to user's Downloads folder
download_dir = os.path.expanduser('~/Downloads')

# Ensure download directory exists
os.makedirs(download_dir, exist_ok=True)

# Build output template path
ydl_opts = {
    # Proxy configuration
    'proxy': 'http://127.0.0.1:7890',
    # Add SSL configuration
    'nocheckcertificate': True,
    # Increase retry count
    'retries': 10,
    # Set timeout
    'socket_timeout': 30,
    # Download audio format
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    # Set download directory
    'outtmpl': os.path.join(download_dir, '%(title)s [%(id)s].%(ext)s')
}

print(f"Starting audio download...")
print(f"Download files will be saved to: {download_dir}")
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    try:
        error_code = ydl.download(URLS)
        if error_code == 0:
            print("Audio download completed successfully!")
        else:
            print(f"Error occurred during audio download, error code: {error_code}")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")