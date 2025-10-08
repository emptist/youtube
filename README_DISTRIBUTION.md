# Application Distribution Structure

I've consolidated all the built applications into a single location for easier management.

## Current Structure

- **/Users/jk/gits/hub/youtube/dist/** - Symbolic link to the consolidated distribution directory
- **/Users/jk/gits/hub/youtube/consolidated_dist/** - Contains all built applications

## Applications Available

1. **denoise_app.app** - Single file audio denoise application
2. **denoise_batch_app.app** - Batch audio denoise application for processing multiple files
3. **simple_downloader.app** - YouTube downloader with noise reduction functionality (fixed version)

## How to Use

Simply navigate to `/Users/jk/gits/hub/youtube/dist/` and double-click any of the .app files to launch the applications.

## Benefits of This Structure

- All applications in one convenient location
- Easy to back up or distribute all applications at once
- Clean separation between source code and compiled applications
- No duplicated application files across multiple directories