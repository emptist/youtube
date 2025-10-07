#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import time
import shutil

# Import the noise reduction function
from de_noise import reduce_noise

class AudioDenoiseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Noise Reduction Tool")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Track if denoising is in progress
        self.denoise_in_progress = False
        
        # Selected file paths
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        
        # Noise reduction parameters
        self.noise_duration = tk.DoubleVar(value=2.0)
        self.chunk_duration = tk.DoubleVar(value=30.0)
        self.keep_original = tk.BooleanVar(value=True)
        
        # Create GUI components
        self.create_widgets()
        
        # Check for ffmpeg
        self.check_ffmpeg_installation()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input file section
        input_frame = ttk.LabelFrame(main_frame, text="Input Audio File", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_file_path, width=70)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_input_button = ttk.Button(input_frame, text="Browse", command=self.browse_input_file)
        browse_input_button.pack(side=tk.LEFT)
        
        # Output file section
        output_frame = ttk.LabelFrame(main_frame, text="Output File", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_file_path, width=70)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_output_button = ttk.Button(output_frame, text="Browse", command=self.browse_output_file)
        browse_output_button.pack(side=tk.LEFT)
        
        # Settings section
        settings_frame = ttk.LabelFrame(main_frame, text="Noise Reduction Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Noise sample duration
        noise_frame = ttk.Frame(settings_frame)
        noise_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(noise_frame, text="Noise Sample Duration (seconds):", width=30).pack(side=tk.LEFT, padx=(0, 10))
        noise_spinbox = ttk.Spinbox(noise_frame, from_=0.5, to=10.0, increment=0.5, textvariable=self.noise_duration, width=10)
        noise_spinbox.pack(side=tk.LEFT)
        
        # Chunk duration
        chunk_frame = ttk.Frame(settings_frame)
        chunk_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(chunk_frame, text="Processing Chunk Duration (seconds):", width=30).pack(side=tk.LEFT, padx=(0, 10))
        chunk_spinbox = ttk.Spinbox(chunk_frame, from_=10.0, to=300.0, increment=10.0, textvariable=self.chunk_duration, width=10)
        chunk_spinbox.pack(side=tk.LEFT)
        
        # Options
        options_frame = ttk.Frame(settings_frame)
        options_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Checkbutton(options_frame, text="Keep original file (don't overwrite)", variable=self.keep_original).pack(anchor=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.denoise_button = ttk.Button(button_frame, text="Apply Noise Reduction", command=self.start_denoise)
        self.denoise_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_denoise, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Processing Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, height=10)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.config(state=tk.DISABLED)
        
        # Bottom info bar
        self.info_var = tk.StringVar(value="Ready. Select an audio file and click Apply Noise Reduction.")
        info_bar = ttk.Label(self.root, textvariable=self.info_var, relief=tk.SUNKEN, anchor=tk.W)
        info_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def browse_input_file(self):
        file_types = [
            ("Audio Files", "*.m4a *.mp3 *.wav *.flac *.ogg *.aac"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            self.input_file_path.set(file_path)
            # Auto-set output path
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            name_without_ext, ext = os.path.splitext(base_name)
            output_path = os.path.join(dir_name, f"{name_without_ext}_denoised{ext}")
            self.output_file_path.set(output_path)
    
    def browse_output_file(self):
        file_types = [
            ("Audio Files", "*.m4a *.mp3 *.wav *.flac *.ogg *.aac"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.asksaveasfilename(filetypes=file_types)
        if file_path:
            self.output_file_path.set(file_path)
    
    def check_ffmpeg_installation(self):
        try:
            # Check if ffmpeg is available
            if os.system('which ffmpeg > /dev/null 2>&1') != 0:
                self.log_message("Warning: ffmpeg is not detected! Some audio formats may not be supported.")
                self.log_message("Please install ffmpeg for best results.")
            else:
                self.log_message("ffmpeg installation detected")
        except Exception as e:
            self.log_message(f"Error checking ffmpeg: {str(e)}")
    
    def start_denoise(self):
        input_file = self.input_file_path.get().strip()
        output_file = self.output_file_path.get().strip()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input audio file.")
            return
        
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file.")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", f"Input file not found: {input_file}")
            return
        
        # Check if output file exists and handle accordingly
        if os.path.exists(output_file) and self.keep_original.get():
            messagebox.showerror("Error", f"Output file already exists: {output_file}\nPlease choose a different name or uncheck 'Keep original file'.")
            return
        
        # Update UI state
        self.denoise_in_progress = True
        self.denoise_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        # Start denoising in a separate thread
        threading.Thread(target=self.process_denoise, args=(input_file, output_file), daemon=True).start()
    
    def cancel_denoise(self):
        self.denoise_in_progress = False
        self.log_message("Denoising cancelled.")
        self.denoise_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
    
    def process_denoise(self, input_file, output_file):
        try:
            self.log_message(f"Starting noise reduction for: {os.path.basename(input_file)}")
            self.log_message(f"Noise sample duration: {self.noise_duration.get()} seconds")
            self.log_message(f"Processing chunk duration: {self.chunk_duration.get()} seconds")
            
            start_time = time.time()
            
            # Call the noise reduction function
            result_file = reduce_noise(
                input_file,
                noise_duration=self.noise_duration.get(),
                chunk_duration=self.chunk_duration.get(),
                output_file=output_file
            )
            
            total_time = time.time() - start_time
            
            self.log_message(f"Noise reduction completed in {total_time:.2f} seconds")
            self.log_message(f"Denoised audio saved to: {os.path.basename(result_file)}")
            
            # Show completion message
            self.root.after(100, lambda: messagebox.showinfo("Success", f"Noise reduction completed successfully!\nFile saved to: {result_file}"))
            
        except Exception as e:
            error_msg = f"Error during noise reduction: {str(e)}"
            self.log_message(error_msg)
            self.root.after(100, lambda: messagebox.showerror("Error", error_msg))
        finally:
            # Update UI state
            self.denoise_in_progress = False
            self.root.after(100, self.reset_ui)
    
    def reset_ui(self):
        self.denoise_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_var.set(100)
    
    def log_message(self, message):
        """Add a message to the status log"""
        self.root.after(100, lambda: self._update_log(message))
    
    def _update_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.info_var.set(message)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioDenoiseApp(root)
    root.mainloop()