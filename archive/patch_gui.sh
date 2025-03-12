#!/bin/bash

# Define the file to patch
FILE_DIR=$(find 'venv/' -name "remi" -type d)
FILE="$FILE_DIR/gui.py"

# Check if the file exists
if [ ! -f "$FILE" ]; then
    echo "File $FILE does not exist."
    exit 1
fi

cp $FILE $FILE.bak
echo "Backup created: $FILE.bak"

cp ./gui.py $FILE
echo "Patched $FILE successfully."