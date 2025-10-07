#!/usr/bin/env python3
import os
import sys
import stat

def make_script_executable(file_path):
    """Make a Python script executable by adding a shebang and setting permissions"""
    try:
        # Read the existing content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if shebang already exists
        if not content.startswith('#!'):
            # Add shebang for Python 3
            new_content = '#!/usr/bin/env python3\n' + content
            
            # Write the new content back to the file
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            print(f"Added shebang to {file_path}")
        else:
            print(f"Shebang already exists in {file_path}")
        
        # Make the file executable
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IEXEC)
        print(f"Set executable permissions for {file_path}")
        
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def create_launcher_script(app_name, script_path):
    """Create a simple launcher script for the application"""
    launcher_path = os.path.join(os.path.dirname(script_path), f"launch_{app_name}.sh")
    try:
        with open(launcher_path, 'w') as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"cd '{os.path.dirname(script_path)}'\n")
            f.write(f"python3 '{os.path.basename(script_path)}'\n")
            f.write(f"exit_code=$?\n")
            f.write(f"echo 'Application exited with code $exit_code'\n")
            f.write(f"read -p 'Press Enter to continue...'\n")
        
        # Make the launcher executable
        st = os.stat(launcher_path)
        os.chmod(launcher_path, st.st_mode | stat.S_IEXEC)
        print(f"Created launcher script: {launcher_path}")
        
        return True
    except Exception as e:
        print(f"Error creating launcher for {app_name}: {str(e)}")
        return False

def main():
    # List of applications to process
    apps = [
        {'name': 'denoise_app', 'script': 'denoise_app.py'},
        {'name': 'denoise_batch_app', 'script': 'denoise_batch_app.py'},
        {'name': 'simple_downloader', 'script': 'simple_downloader.py'},
        {'name': 'standalone_simple_downloader', 'script': os.path.join('standalone_app', 'simple_downloader.py')}
    ]
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Making audio processing applications executable...\n")
    
    # Process each application
    for app in apps:
        script_path = os.path.join(current_dir, app['script'])
        
        if os.path.exists(script_path):
            print(f"Processing {app['name']}...")
            
            # Make the Python script executable
            success = make_script_executable(script_path)
            
            # Create a launcher script
            if success:
                create_launcher_script(app['name'], script_path)
            
            print()
        else:
            print(f"Skipping {app['name']}: File not found at {script_path}\n")
    
    print("Process completed!")
    print("\nUsage instructions:")
    print("1. You can now run the applications by double-clicking the launcher scripts")
    print("2. Alternatively, run them from the command line using:\n   ./denoise_app.py\n   ./denoise_batch_app.py")
    print("\nNote: If double-clicking doesn't work, open a terminal and run:\n   chmod +x *.py *.sh standalone_app/*.py")

if __name__ == "__main__":
    main()