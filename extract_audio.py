import yt_dlp
import ssl
import os
import yt_dlp

# Configure SSL context to handle potential certificate issues
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

URLS = [
    'https://www.youtube.com/watch?v=BUJpAzByMjo&t=279s'
]

# Check if ffmpeg is installed
has_ffmpeg = False
try:
    # Try to find ffmpeg in PATH
    if os.system('which ffmpeg > /dev/null 2>&1') == 0:
        has_ffmpeg = True
        print("ffmpeg installation detected")
    else:
        print("ffmpeg installation not detected")
except Exception:
    print("Error checking ffmpeg installation status")

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
    # Don't use postprocessor to avoid ffmpeg dependency
    'postprocessors': [],
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
            if not has_ffmpeg:
                print("Note: ffmpeg is not installed, so no audio post-processing was performed.")
                print("It is recommended to install ffmpeg for better audio quality and compatibility.")
                print("Installation command example (Homebrew): brew install ffmpeg")
        else:
            print(f"Error occurred during audio download, error code: {error_code}")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")