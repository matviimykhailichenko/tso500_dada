#!/bin/bash

# Define the target directory
TARGET_DIR="/staging/test_transfer_results_cbmed"

# Create the directory structure
mkdir -p "$TARGET_DIR/work"
mkdir -p "$TARGET_DIR/errors"
mkdir -p "$TARGET_DIR/Results"
mkdir -p "$TARGET_DIR/Logs_Intermediates"
mkdir -p "$TARGET_DIR/.nextflow"

# Create the files with placeholder content
touch "$TARGET_DIR/receipt"
touch "$TARGET_DIR/inputs.json"
touch "$TARGET_DIR/analysis.log"
touch "$TARGET_DIR/SampleSheet.csv"

# Set file sizes (optional, for realism)
echo "Sample receipt content" > "$TARGET_DIR/receipt"
echo '{"key": "value"}' > "$TARGET_DIR/inputs.json"
head -c 201600 "$TARGET_DIR/analysis.log" > /dev/null
echo "Sample,Data,Here" > "$TARGET_DIR/SampleSheet.csv"

# Set permissions to match the screenshot (-rwxr-xr-x for files, drwxr-xr-x for directories)
chmod 755 "$TARGET_DIR/receipt" "$TARGET_DIR/inputs.json" "$TARGET_DIR/analysis.log" "$TARGET_DIR/SampleSheet.csv"
chmod 755 "$TARGET_DIR/work" "$TARGET_DIR/errors" "$TARGET_DIR/Results" "$TARGET_DIR/Logs_Intermediates" "$TARGET_DIR/.nextflow"

echo "Directory structure and files created in $TARGET_DIR"
