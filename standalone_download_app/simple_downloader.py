#!/usr/bin/env python3
import ssl
import os
import sys
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import subprocess
import re
import urllib.request
import shutil

# Lazy imports for heavy libraries
yt_dlp = None
reduce_noise = None

def _import_heavy_libraries():
    """Lazily import heavy libraries when needed"""
    global yt_dlp, reduce_noise
    if yt_dlp is None:
        import yt_dlp
    if reduce_noise is None:
        from de_noise import reduce_noise
    return yt_dlp, reduce_noise

class SimpleYouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple YouTube Downloader")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Set default download directory to user's Downloads folder
        self.download_dir = os.path.expanduser('~/Downloads')
        
        # Configure SSL context to handle potential certificate issues
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Track if download is in progress
        self.download_in_progress = False
        
        # Proxy settings
        self.system_proxy = self.detect_system_proxy()
        self.use_system_proxy = tk.BooleanVar(value=bool(self.system_proxy))
        self.use_custom_proxy = tk.BooleanVar(value=False)
        self.custom_proxy_url = tk.StringVar(value="http://127.0.0.1:7890")
        
        # Download type (audio or video)
        self.download_type = tk.StringVar(value="audio")
        
        # Format selection
        self.format_var = tk.StringVar(value="m4a")
        
        # Noise reduction options
        self.apply_denoise = tk.BooleanVar(value=False)
        self.keep_original_audio = tk.BooleanVar(value=True)
        
        # Initialize ffmpeg status to False before GUI creation
        self.has_ffmpeg = False
        
        # Create GUI components
        self.create_widgets()
        
        # Now check for ffmpeg installation after GUI is ready
        self.check_ffmpeg_installation()
        
        # Log proxy detection result
        if self.system_proxy:
            self.log_message(f"System proxy detected: {self.system_proxy}")
        else:
            self.log_message("No system proxy detected")
    
    def detect_system_proxy(self):
        """Detect system proxy settings"""
        try:
            # Get system proxy settings from urllib
            proxies = urllib.request.getproxies()
            # Check for http proxy
            if 'http' in proxies:
                return proxies['http']
            # Check for https proxy
            elif 'https' in proxies:
                return proxies['https']
            # Check for all_proxy
            elif 'all_proxy' in proxies:
                return proxies['all_proxy']
            # Check for ALL_PROXY
            elif 'ALL_PROXY' in proxies:
                return proxies['ALL_PROXY']
            return None
        except Exception:
            return None
    
    def create_widgets(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL input section
        url_frame = ttk.LabelFrame(main_frame, text="YouTube URL", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.url_entry = ttk.Entry(url_frame, width=80)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=")
        
        paste_button = ttk.Button(url_frame, text="Paste", command=self.paste_url)
        paste_button.pack(side=tk.LEFT)
        
        # Download directory section
        dir_frame = ttk.LabelFrame(main_frame, text="Download Directory", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dir_entry = ttk.Entry(dir_frame, width=70)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.dir_entry.insert(0, self.download_dir)
        
        browse_button = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_button.pack(side=tk.LEFT)
        
        # Download type selection
        type_frame = ttk.LabelFrame(main_frame, text="Download Type", padding="10")
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(type_frame, text="Audio Only", variable=self.download_type, value="audio", command=self.toggle_format_options).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="Video with Audio (Single File)", variable=self.download_type, value="video", command=self.toggle_format_options).pack(side=tk.LEFT, padx=10)
        
        # Format selection
        self.format_frame = ttk.LabelFrame(main_frame, text="Format Options", padding="10")
        self.format_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.format_var = tk.StringVar(value="m4a")
        self.m4a_radio = ttk.Radiobutton(self.format_frame, text="M4A (High Quality)", variable=self.format_var, value="m4a")
        self.m4a_radio.pack(side=tk.LEFT, padx=10)
        self.mp3_radio = ttk.Radiobutton(self.format_frame, text="MP3 (Compatibility)", variable=self.format_var, value="mp3")
        self.mp3_radio.pack(side=tk.LEFT, padx=10)
        
        # Noise reduction options
        self.denoise_frame = ttk.LabelFrame(main_frame, text="Audio Enhancement", padding="10")
        self.denoise_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.denoise_checkbox = ttk.Checkbutton(
            self.denoise_frame,
            text="Apply Noise Reduction",
            variable=self.apply_denoise
        )
        self.denoise_checkbox.pack(anchor=tk.W, pady=(0, 5))
        
        self.keep_original_checkbox = ttk.Checkbutton(
            self.denoise_frame,
            text="Keep Original Audio File",
            variable=self.keep_original_audio
        )
        self.keep_original_checkbox.pack(anchor=tk.W, pady=(0, 5))
        
        # Proxy settings
        proxy_frame = ttk.LabelFrame(main_frame, text="Proxy Settings", padding="10")
        proxy_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Use system proxy checkbox
        ttk.Checkbutton(
            proxy_frame, 
            text="Use System Proxy", 
            variable=self.use_system_proxy, 
            command=self.toggle_proxy_options
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Use custom proxy checkbox
        self.custom_proxy_check = ttk.Checkbutton(
            proxy_frame, 
            text="Use Custom Proxy", 
            variable=self.use_custom_proxy, 
            command=self.toggle_proxy_options
        )
        self.custom_proxy_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Custom proxy URL entry
        proxy_entry_frame = ttk.Frame(proxy_frame)
        proxy_entry_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(proxy_entry_frame, text="Proxy URL:").pack(side=tk.LEFT, padx=(20, 5))
        self.proxy_entry = ttk.Entry(proxy_entry_frame, textvariable=self.custom_proxy_url, width=50)
        self.proxy_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.proxy_entry.config(state=tk.DISABLED)  # Initially disabled
        
        # Call toggle_format_options to set initial state
        self.toggle_format_options()
        # Call toggle_proxy_options to set initial proxy state
        self.toggle_proxy_options()
        
        # Download button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.download_button = ttk.Button(button_frame, text="Download", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, height=10)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.config(state=tk.DISABLED)
        
        # Bottom info bar
        self.info_var = tk.StringVar(value="Ready. Please enter a YouTube URL and click Download.")
        info_bar = ttk.Label(self.root, textvariable=self.info_var, relief=tk.SUNKEN, anchor=tk.W)
        info_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def toggle_proxy_options(self):
        """Toggle the state of proxy options based on user selections"""
        if self.use_system_proxy.get():
            # Disable custom proxy options if system proxy is selected
            self.use_custom_proxy.set(False)
            self.custom_proxy_check.config(state=tk.DISABLED)
            self.proxy_entry.config(state=tk.DISABLED)
        else:
            self.custom_proxy_check.config(state=tk.NORMAL)
            
            if self.use_custom_proxy.get():
                self.proxy_entry.config(state=tk.NORMAL)
            else:
                self.proxy_entry.config(state=tk.DISABLED)
                
    def toggle_format_options(self):
        """Toggle format options based on download type selection"""
        if self.download_type.get() == "audio":
            self.m4a_radio.config(state=tk.NORMAL)
            self.mp3_radio.pack(side=tk.LEFT, padx=10)  # Make MP3 option visible
            self.mp3_radio.config(state=tk.NORMAL)
            self.format_frame.config(text="Audio Format Options")
            # Enable noise reduction options for audio
            # LabelFrame doesn't support state option, so just enable the widgets inside
            self.denoise_checkbox.config(state=tk.NORMAL)
            self.keep_original_checkbox.config(state=tk.NORMAL)
        else:
            # For video downloads, hide audio format options
            self.m4a_radio.config(state=tk.DISABLED)
            self.mp3_radio.pack_forget()  # Hide MP3 option
            self.format_frame.config(text="Video will be downloaded in MP4 format")
            # Disable noise reduction options for video
            # LabelFrame doesn't support state option, so just disable the widgets inside
            self.denoise_checkbox.config(state=tk.DISABLED)
            self.keep_original_checkbox.config(state=tk.DISABLED)
    
    def paste_url(self):
        # Clear current entry
        self.url_entry.delete(0, tk.END)
        # Paste from clipboard
        try:
            url = self.root.clipboard_get()
            self.url_entry.insert(0, url)
        except tk.TclError:
            messagebox.showerror("Error", "Nothing to paste from clipboard")
    
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.download_dir)
        if directory:
            self.download_dir = directory
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
    
    def check_ffmpeg_installation(self):
        try:
            # Add parent directory to Python path to import ffmpeg_utils
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Import the shared ffmpeg utility
            from ffmpeg_utils import check_ffmpeg, get_ffmpeg_path
            
            # Use the shared utility to check for ffmpeg
            is_installed, message = check_ffmpeg()
            
            if is_installed:
                self.has_ffmpeg = True
                ffmpeg_path = get_ffmpeg_path()
                if ffmpeg_path:
                    self.log_message(f"ffmpeg installation detected at {ffmpeg_path}. Audio conversion available.")
                else:
                    self.log_message("ffmpeg installation detected. Audio conversion available.")
            else:
                self.has_ffmpeg = False
                self.log_message(f"ERROR: {message}")
        except Exception as e:
            self.has_ffmpeg = False
            self.log_message(f"ERROR: ffmpeg is required but error occurred: {str(e)}")
    
    def log_message(self, message):
        self.status_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.info_var.set(message)
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url or "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        # Check if directory exists
        if not os.path.exists(self.download_dir):
            try:
                os.makedirs(self.download_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create directory: {str(e)}")
                return
        
        # Disable download button and enable cancel button
        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.download_in_progress = True
        
        # Start appropriate download method based on selection
        if self.download_type.get() == "audio":
            threading.Thread(target=self.download_audio, args=(url,), daemon=True).start()
        else:
            threading.Thread(target=self.download_video, args=(url,), daemon=True).start()
    
    def cancel_download(self):
        self.download_in_progress = False
        self.log_message("Download cancelled.")
        self.download_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
    
    def download_audio(self, url):
        try:
            self.log_message(f"Starting audio download from: {url}")
            
            # Build yt-dlp options
            format = self.format_var.get()
            
            # Set up format selection - prefer M4A for better quality when possible
            if format == "m4a":
                format_str = 'bestaudio[ext=m4a]/bestaudio/best'
            else:  # mp3
                format_str = 'bestaudio'
            
            # Determine proxy settings
            proxy = None
            if self.use_system_proxy.get() and self.system_proxy:
                proxy = self.system_proxy
                self.log_message(f"Using system proxy: {proxy}")
            elif self.use_custom_proxy.get():
                proxy = self.custom_proxy_url.get().strip()
                if proxy:
                    self.log_message(f"Using custom proxy: {proxy}")
                else:
                    self.log_message("Custom proxy URL is empty, not using proxy")
            else:
                self.log_message("Not using proxy")
            
            ydl_opts = {
                # Add SSL configuration
                'nocheckcertificate': True,
                # Increase retry count
                'retries': 10,
                # Set timeout
                'socket_timeout': 30,
                # Download audio format
                'format': format_str,
                # Progress hook for updates
                'progress_hooks': [self.update_progress],
                # Set download directory
                'outtmpl': os.path.join(self.download_dir, '%(title)s [%(id)s].%(ext)s'),
                # Quiet output to prevent console spam
                'quiet': True,
                'no_warnings': True,
                # Ensure ffmpeg is used for postprocessing even when running standalone
                'ffmpeg_location': shutil.which('ffmpeg') or '',
            }
            
            # Add proxy if configured
            if proxy:
                ydl_opts['proxy'] = proxy
            
            # If we want MP3, use postprocessor to convert
            if format == "mp3":
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                # No postprocessors needed for M4A format
                ydl_opts['postprocessors'] = []
            
            # Import heavy libraries when needed
            yt_dlp_lib, reduce_noise_func = _import_heavy_libraries()
            with yt_dlp_lib.YoutubeDL(ydl_opts) as ydl:
                # Check if download was cancelled before starting
                if not self.download_in_progress:
                    return
                
                # Extract video info first to get title
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                self.log_message(f"Downloading: {title}")
                
                # Start the actual download
                ydl.download([url])
                
                # If download was cancelled during process
                if not self.download_in_progress:
                    return
                
                # Get the actual filename
                filename = ydl.prepare_filename(info)
                
                # If noise reduction is requested, process the file
                if self.apply_denoise.get():
                    self.log_message("Starting noise reduction process...")
                    
                    # No need to create a raw version as we'll keep the original file directly
                    if self.keep_original_audio.get():
                        self.log_message(f"Will keep original audio file: {os.path.basename(filename)}")
                    
                    try:
                        # Apply noise reduction
                        denoised_file = reduce_noise_func(filename)
                        self.log_message(f"Noise reduction completed: {os.path.basename(denoised_file)}")
                        
                        # Always keep the '_denoised' suffix for clarity
                        if not self.keep_original_audio.get():
                            # Keep the denoised file with its suffix
                            # Just remove the original file without renaming
                            os.remove(filename)
                            self.log_message(f"Final denoised audio saved as: {os.path.basename(denoised_file)}")
                    except Exception as e:
                        self.log_message(f"Error during noise reduction: {str(e)}")
                
                self.log_message(f"Download completed: {os.path.basename(filename)}")
                self.log_message(f"File saved to: {self.download_dir}")
                
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
        finally:
            # Reset UI state
            self.root.after(0, self.reset_ui)
                
    def download_video(self, url):
        try:
            self.log_message(f"Starting video download from: {url}")
            self.log_message("Note: Video files may be large, please ensure you have enough disk space.")
            
            # Determine proxy settings
            proxy = None
            if self.use_system_proxy.get() and self.system_proxy:
                proxy = self.system_proxy
                self.log_message(f"Using system proxy: {proxy}")
            elif self.use_custom_proxy.get():
                proxy = self.custom_proxy_url.get().strip()
                if proxy:
                    self.log_message(f"Using custom proxy: {proxy}")
                else:
                    self.log_message("Custom proxy URL is empty, not using proxy")
            else:
                self.log_message("Not using proxy")
            
            ydl_opts = {
                # Add SSL configuration
                'nocheckcertificate': True,
                # Increase retry count
                'retries': 10,
                # Set timeout
                'socket_timeout': 30,
                # Download merged video format (MP4 is preferred)
                'format': 'best[ext=mp4]/best',
                # Disable automatic merging feature
                'merge_output_format': None,
                # No postprocessors for video
                'postprocessors': [],
                # Progress hook for updates
                'progress_hooks': [self.update_progress],
                # Set download directory
                'outtmpl': os.path.join(self.download_dir, '%(title)s [%(id)s].%(ext)s'),
                # Quiet output to prevent console spam
                'quiet': True,
                'no_warnings': True,
            }
            
            # Add proxy if configured
            if proxy:
                ydl_opts['proxy'] = proxy
            
            # Import heavy libraries when needed
            yt_dlp_lib, _ = _import_heavy_libraries()
            with yt_dlp_lib.YoutubeDL(ydl_opts) as ydl:
                # Check if download was cancelled before starting
                if not self.download_in_progress:
                    return
                
                # Extract video info first to get title
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                self.log_message(f"Downloading video: {title}")
                
                # Start the actual download
                ydl.download([url])
                
                # If download was cancelled during process
                if not self.download_in_progress:
                    return
                
                # Get the actual filename
                filename = ydl.prepare_filename(info)
                
                self.log_message(f"Video download completed: {os.path.basename(filename)}")
                self.log_message(f"File saved to: {self.download_dir}")
                self.log_message("Video remains in original format and quality, no conversion needed.")
                
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            # Reset UI state
            self.root.after(0, self.reset_ui)
    
    def update_progress(self, d):
        if d['status'] == 'downloading':
            # Calculate progress percentage
            if d.get('total_bytes'):
                percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress_var.set(percentage)
            
            # Update status message with speed
            speed = d.get('speed', 0)
            if speed:
                speed_mb = speed / (1024 * 1024)
                self.info_var.set(f"Downloading... {speed_mb:.2f} MB/s")
        elif d['status'] == 'finished':
            self.progress_var.set(100)
            self.info_var.set("Processing final file...")
    
    def reset_ui(self):
        self.download_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.download_in_progress = False
        if self.progress_var.get() == 100:
            self.root.after(2000, lambda: self.progress_var.set(0))

if __name__ == "__main__":
    # Set up Tkinter root window
    root = tk.Tk()
    
    # Create and run the application
    app = SimpleYouTubeDownloader(root)
    root.mainloop()