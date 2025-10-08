#!/bin/bash
cd '/Users/jk/gits/hub/youtube/standalone_app'
python3 'simple_downloader.py'
exit_code=$?
echo 'Application exited with code $exit_code'
read -p 'Press Enter to continue...'
