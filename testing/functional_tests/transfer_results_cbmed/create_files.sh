#!/bin/bash

# Define the target directory
TARGET_DIR="/staging/test_results_dir"

# Create the main work directory
mkdir -p "$TARGET_DIR/work"

# List of directories to create (from the screenshot)
DIRS=("fe" "fb" "f4" "f2" "ec" "e2" "e0" "df" "dd" "d6" "d3" "d1" "bd" "b8" "b4" "ae" "ab" "aa" "a9" "a5" "a4" "9c" "9b" "99" "98" "97" "96" "93" "92" "8d")

# Create each directory and populate with random files
for dir in "${DIRS[@]}"; do
  mkdir -p "$TARGET_DIR/work/$dir"

  # Generate 1-3 random files in each directory
  NUM_FILES=$((RANDOM % 3 + 1))

  for ((i=1; i<=NUM_FILES; i++)); do
    # Create a random file with random content
    dd if=/dev/urandom of="$TARGET_DIR/work/$dir/file_$i.dat" bs=1K count=$((RANDOM % 10 + 1)) 2>/dev/null
  done
done

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

# Define the target directory
TARGET_DIR="/staging/test_run_files_dir"

# Create the directory structure
mkdir -p "$TARGET_DIR/Thumbnail_Images"
mkdir -p "$TARGET_DIR/Recipe"
mkdir -p "$TARGET_DIR/Logs"
mkdir -p "$TARGET_DIR/InterOp"
mkdir -p "$TARGET_DIR/Data"
mkdir -p "$TARGET_DIR/Config"

# Create the files with placeholder content
touch "$TARGET_DIR/SequenceComplete.txt"
touch "$TARGET_DIR/RunParameters.xml"
touch "$TARGET_DIR/RunInfo.xml"
touch "$TARGET_DIR/RTAComplete.txt"
touch "$TARGET_DIR/RTA3.cfg"
touch "$TARGET_DIR/CopyComplete.txt"
touch "$TARGET_DIR/ANALYZED.txt"

# Set file sizes (optional, for realism)
echo "" > "$TARGET_DIR/SequenceComplete.txt"
echo "<RunParameters></RunParameters>" > "$TARGET_DIR/RunParameters.xml"
head -c 36100 /dev/zero > "$TARGET_DIR/RunInfo.xml"
echo "" > "$TARGET_DIR/RTAComplete.txt"
head -c 11900 /dev/zero > "$TARGET_DIR/RTA3.cfg"
echo "" > "$TARGET_DIR/CopyComplete.txt"
echo "" > "$TARGET_DIR/ANALYZED.txt"

# Set permissions to match the screenshot (-rwxr-xr-x for files, drwxr-xr-x for directories)
chmod 755 "$TARGET_DIR/SequenceComplete.txt" "$TARGET_DIR/RunParameters.xml" "$TARGET_DIR/RunInfo.xml" \
    "$TARGET_DIR/RTAComplete.txt" "$TARGET_DIR/RTA3.cfg" "$TARGET_DIR/CopyComplete.txt" "$TARGET_DIR/ANALYZED.txt"

chmod 755 "$TARGET_DIR/Thumbnail_Images" "$TARGET_DIR/Recipe" "$TARGET_DIR/Logs" \
    "$TARGET_DIR/InterOp" "$TARGET_DIR/Data" "$TARGET_DIR/Config"

echo "Directory structure and files created in $TARGET_DIR"