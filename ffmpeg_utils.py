#!/usr/bin/env python3
import os
import subprocess
import shutil

class FFmpegUtils:
    @staticmethod
    def check_ffmpeg():
        """Check if ffmpeg is installed with multiple detection methods.
        
        Returns:
            tuple: (is_installed, message)
                is_installed: Boolean indicating if ffmpeg was found
                message: String with details about the detection result
        """
        try:
            # Method 1: Direct command execution
            try:
                subprocess.run(
                    ['ffmpeg', '-version'], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    check=True
                )
                return True, "ffmpeg installation detected"
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
            
            # Method 2: Check common installation paths based on OS
            common_paths = []
            if os.name == 'posix':  # macOS/Linux
                common_paths = [
                    '/usr/local/bin/ffmpeg', 
                    '/opt/homebrew/bin/ffmpeg', 
                    '/usr/bin/ffmpeg', 
                    '/bin/ffmpeg'
                ]
            elif os.name == 'nt':  # Windows
                common_paths = [
                    os.path.join(os.environ.get('ProgramFiles', ''), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                    os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'ffmpeg', 'bin', 'ffmpeg.exe')
                ]
            
            for path in common_paths:
                if path and os.path.isfile(path) and os.access(path, os.X_OK):
                    return True, f"ffmpeg detected at: {path}"
            
            # Method 3: Use shutil.which to check PATH (more cross-platform)
            ffmpeg_path = shutil.which('ffmpeg')
            if ffmpeg_path:
                return True, f"ffmpeg detected at: {ffmpeg_path}"
            
            # Method 4: System-specific PATH checking (which/where)
            if os.name == 'posix':  # macOS/Linux
                result = os.system('which ffmpeg > /dev/null 2>&1')
                if result == 0:
                    path = subprocess.check_output(['which', 'ffmpeg']).decode('utf-8').strip()
                    return True, f"ffmpeg detected at: {path}"
            elif os.name == 'nt':  # Windows
                result = os.system('where ffmpeg > NUL 2>&1')
                if result == 0:
                    path = subprocess.check_output(['where', 'ffmpeg']).decode('utf-8').strip()
                    return True, f"ffmpeg detected at: {path}"
            
            # If all methods fail
            error_msg = (
                "ffmpeg is required but not detected!\n"
                "Please install ffmpeg and ensure it's in your system PATH.\n"
                "Installation instructions:\n"
                "- macOS: brew install ffmpeg\n"
                "- Windows: Download from https://ffmpeg.org/download.html\n"
                "- Linux: Use your package manager (e.g., sudo apt install ffmpeg)"
            )
            return False, error_msg
        
        except Exception as e:
            return False, f"Error checking ffmpeg: {str(e)}"
    
    @staticmethod
    def get_ffmpeg_path():
        """Get the path to the ffmpeg executable if available.
        
        Returns:
            str or None: Path to ffmpeg executable if found, None otherwise
        """
        # Try shutil.which first (most cross-platform)
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
        
        # Check common installation paths
        common_paths = []
        if os.name == 'posix':  # macOS/Linux
            common_paths = [
                '/usr/local/bin/ffmpeg', 
                '/opt/homebrew/bin/ffmpeg', 
                '/usr/bin/ffmpeg', 
                '/bin/ffmpeg'
            ]
        elif os.name == 'nt':  # Windows
            common_paths = [
                os.path.join(os.environ.get('ProgramFiles', ''), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'ffmpeg', 'bin', 'ffmpeg.exe')
            ]
        
        for path in common_paths:
            if path and os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        return None
    
    @staticmethod
    def get_installation_instructions():
        """Get platform-specific installation instructions for ffmpeg.
        
        Returns:
            str: Installation instructions
        """
        instructions = "Installation instructions:\n"
        if os.name == 'posix':
            if sys.platform == 'darwin':  # macOS
                instructions += "- macOS: brew install ffmpeg\n"
            else:  # Linux
                instructions += "- Linux: Use your package manager (e.g., sudo apt install ffmpeg)\n"
        elif os.name == 'nt':  # Windows
            instructions += "- Windows: Download from https://ffmpeg.org/download.html\n"
        
        return instructions

# Add import sys for platform detection
import sys

# Create a singleton instance for easier use
ffmpeg_utils = FFmpegUtils()

# Convenience functions to use with the singleton
check_ffmpeg = ffmpeg_utils.check_ffmpeg
get_ffmpeg_path = ffmpeg_utils.get_ffmpeg_path
get_installation_instructions = ffmpeg_utils.get_installation_instructions