#!/bin/bash
cd '/Users/jk/gits/hub/youtube'
python3 'denoise_batch_app.py'
exit_code=$?
echo 'Application exited with code $exit_code'
read -p 'Press Enter to continue...'
