import yt_dlp
import ssl
import os
import sys

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

# Configure SSL context to handle potential certificate issues
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# YouTube video URL list
URLS = [
    'https://www.youtube.com/watch?v=BUJpAzByMjo&t=279s'
]

# Set download directory to user's Downloads folder
download_dir = os.path.expanduser('~/Downloads')

# Ensure download directory exists
os.makedirs(download_dir, exist_ok=True)

# Video download configuration options
ydl_opts = {
    # Proxy configuration
    'proxy': 'http://127.0.0.1:7890',
    # Add SSL configuration to avoid certificate verification issues
    'nocheckcertificate': True,
    # Increase retry count to improve download stability
    'retries': 10,
    # Set timeout duration
    'socket_timeout': 30,
    # Download best available format
    'format': 'best[ext=mp4]/best',
    # Enable automatic merging when needed
    'merge_output_format': 'mp4',
    # No post-processors needed for basic video download
    'postprocessors': [],
    # Set download directory
    'outtmpl': os.path.join(download_dir, '%(title)s [%(id)s].%(ext)s')
}

def download_video():
    """
    Main function for downloading YouTube videos
    """
    print("Starting video download...")
    print(f"Files will be saved to: {download_dir}")
    print("Note: Video files may be large, please ensure you have enough disk space.")
    print("To interrupt download, press Ctrl+C.")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Ensure using merged video format
            ydl_opts['format'] = 'best[ext=mp4]/best'
            
            error_code = ydl.download(URLS)
            if error_code == 0:
                print("Video download completed successfully!")
                print("Video will remain in original format and quality, no conversion needed.")
            else:
                print(f"Error occurred during video download, error code: {error_code}")
        except KeyboardInterrupt:
            print("\nDownload interrupted by user.")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    download_video()