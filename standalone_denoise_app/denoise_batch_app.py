#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import time
import shutil

# Lazy import for reduce_noise
reduce_noise = None

def _import_reduce_noise():
    global reduce_noise
    if reduce_noise is None:
        from de_noise import reduce_noise
    return reduce_noise

class BatchAudioDenoiseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Audio Noise Reduction Tool")
        self.root.geometry("850x700")
        self.root.resizable(True, True)
        
        # Track if denoising is in progress
        self.denoise_in_progress = False
        self.current_file_index = 0
        self.total_files = 0
        self.selected_files = []
        
        # Noise reduction parameters
        self.noise_duration = tk.DoubleVar(value=2.0)
        self.chunk_duration = tk.DoubleVar(value=30.0)
        self.keep_original = tk.BooleanVar(value=True)
        self.output_dir = tk.StringVar(value="")
        
        # Create GUI components
        self.create_widgets()
        
        # Check for ffmpeg
        self.check_ffmpeg_installation()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection section
        files_frame = ttk.LabelFrame(main_frame, text="Selected Files", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # File list
        self.file_listbox = tk.Listbox(files_frame, selectmode=tk.EXTENDED, width=80, height=10)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Scrollbar for file list
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # File actions frame
        file_actions_frame = ttk.Frame(main_frame)
        file_actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        add_files_button = ttk.Button(file_actions_frame, text="Add Files", command=self.add_files)
        add_files_button.pack(side=tk.LEFT, padx=(0, 10))
        
        remove_files_button = ttk.Button(file_actions_frame, text="Remove Selected", command=self.remove_files)
        remove_files_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_files_button = ttk.Button(file_actions_frame, text="Clear All", command=self.clear_files)
        clear_files_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Output directory
        output_dir_frame = ttk.Frame(main_frame)
        output_dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_dir_frame, text="Output Directory:", width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        self.output_dir_entry = ttk.Entry(output_dir_frame, textvariable=self.output_dir, width=50)
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_dir_button = ttk.Button(output_dir_frame, text="Browse Directory", command=self.browse_output_directory)
        browse_dir_button.pack(side=tk.LEFT, padx=(0, 5))
        
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
        
        ttk.Checkbutton(options_frame, text="Keep original files (don't overwrite)", variable=self.keep_original).pack(anchor=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.denoise_button = ttk.Button(button_frame, text="Apply Noise Reduction to All", command=self.start_batch_denoise)
        self.denoise_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_denoise, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Progress label
        self.progress_label = ttk.Label(main_frame, text="Ready")
        self.progress_label.pack(fill=tk.X, pady=(0, 5))
        
        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Processing Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, height=10)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.config(state=tk.DISABLED)
        
        # Bottom info bar
        self.info_var = tk.StringVar(value="Ready. Add audio files and click Apply Noise Reduction to All.")
        info_bar = ttk.Label(self.root, textvariable=self.info_var, relief=tk.SUNKEN, anchor=tk.W)
        info_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def add_files(self):
        file_types = [
            ("Audio Files", "*.m4a *.mp3 *.wav *.flac *.ogg *.aac"),
            ("All Files", "*.*")
        ]
        file_paths = filedialog.askopenfilenames(filetypes=file_types)
        
        if file_paths:
            # Set output directory if not already set
            if not self.output_dir.get():
                first_dir = os.path.dirname(file_paths[0])
                self.output_dir.set(first_dir)
                
            # Add files to list and listbox
            for file_path in file_paths:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    self.file_listbox.insert(tk.END, os.path.basename(file_path))
            
            self.log_message(f"Added {len(file_paths)} files to the list")
            
    def remove_files(self):
        selected_indices = sorted(self.file_listbox.curselection(), reverse=True)
        if selected_indices:
            for index in selected_indices:
                self.file_listbox.delete(index)
                del self.selected_files[index]
            
            self.log_message(f"Removed {len(selected_indices)} files from the list")
        else:
            messagebox.showinfo("Info", "Please select file(s) to remove")
            
    def clear_files(self):
        self.file_listbox.delete(0, tk.END)
        self.selected_files.clear()
        self.log_message("All files cleared from the list")
        
    def browse_output_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir.get() or os.getcwd())
        if directory:
            self.output_dir.set(directory)
    
    def check_ffmpeg_installation(self):
        try:
            # Add parent directory to Python path to import ffmpeg_utils
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Import the shared ffmpeg utility
            from ffmpeg_utils import check_ffmpeg
            
            # Use the shared utility to check for ffmpeg
            is_installed, message = check_ffmpeg()
            
            if is_installed:
                self.log_message("ffmpeg installation detected")
            else:
                self.log_message(f"Warning: {message}")
        except Exception as e:
            self.log_message(f"Error checking ffmpeg: {str(e)}")
    
    def start_batch_denoise(self):
        # Validate input
        if not self.selected_files:
            messagebox.showerror("Error", "Please add audio files to process.")
            return
            
        output_dir = self.output_dir.get().strip()
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return
            
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output directory: {str(e)}")
                return
        
        # Update UI state
        self.denoise_in_progress = True
        self.current_file_index = 0
        self.total_files = len(self.selected_files)
        self.denoise_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.progress_label.config(text=f"Starting batch processing...")
        
        # Start batch denoising in a separate thread
        threading.Thread(target=self.process_batch_denoise, daemon=True).start()
    
    def cancel_denoise(self):
        self.denoise_in_progress = False
        self.log_message("Batch denoising cancelled.")
        
    def process_batch_denoise(self):
        output_dir = self.output_dir.get().strip()
        success_count = 0
        error_count = 0
        
        try:
            for i, input_file in enumerate(self.selected_files):
                if not self.denoise_in_progress:
                    break
                    
                self.current_file_index = i + 1
                
                # Update progress label
                self.root.after(100, lambda: self.progress_label.config(
                    text=f"Processing file {self.current_file_index}/{self.total_files}: {os.path.basename(input_file)}"))
                
                # Calculate output file path
                base_name = os.path.basename(input_file)
                name_without_ext, ext = os.path.splitext(base_name)
                output_file = os.path.join(output_dir, f"{name_without_ext}_denoised{ext}")
                
                # Check if output file exists and handle accordingly
                if os.path.exists(output_file) and self.keep_original.get():
                    error_msg = f"Skipping {base_name}: Output file already exists."
                    self.log_message(error_msg)
                    error_count += 1
                    continue
                    
                try:
                    self.log_message(f"Starting noise reduction for file {self.current_file_index}/{self.total_files}: {base_name}")
                    
                    start_time = time.time()
                    
                    # Import and call the noise reduction function
                    reduce_noise_func = _import_reduce_noise()
                    result_file = reduce_noise_func(
                        input_file,
                        noise_sample_duration=self.noise_duration.get(),
                        chunk_duration=self.chunk_duration.get(),
                        output_file=output_file
                    )
                    
                    total_time = time.time() - start_time
                    
                    self.log_message(f"Successfully processed {base_name} in {total_time:.2f} seconds")
                    success_count += 1
                    
                except Exception as e:
                    error_msg = f"Error processing {base_name}: {str(e)}"
                    self.log_message(error_msg)
                    error_count += 1
                
                # Update overall progress
                progress_percent = (self.current_file_index / self.total_files) * 100
                self.root.after(100, lambda p=progress_percent: self.progress_var.set(p))
            
            # Show completion summary
            if self.denoise_in_progress:
                summary_msg = f"Batch processing completed!\n"\
                              f"Successfully processed: {success_count}\n"\
                              f"Failed to process: {error_count}"
                self.root.after(100, lambda: messagebox.showinfo("Batch Complete", summary_msg))
                
        except Exception as e:
            error_msg = f"Fatal error during batch processing: {str(e)}"
            self.log_message(error_msg)
            self.root.after(100, lambda: messagebox.showerror("Error", error_msg))
        finally:
            # Update UI state
            self.denoise_in_progress = False
            self.root.after(100, self.reset_ui)
    
    def reset_ui(self):
        self.denoise_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Ready")
    
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
    app = BatchAudioDenoiseApp(root)
    root.mainloop()