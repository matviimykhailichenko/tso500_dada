#!/bin/bash

# Default values
RUN_FOLDER=""
ANALYSIS_FOLDER=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --runFolder)
      RUN_FOLDER="$2"
      shift 2
      ;;
    --analysisFolder)
      ANALYSIS_FOLDER="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check if required parameters are provided
if [ -z "$RUN_FOLDER" ] || [ -z "$ANALYSIS_FOLDER" ]; then
  echo "Usage: $0 --runFolder <run_folder_path> --analysisFolder <analysis_folder_path>"
  exit 1
fi

# Create the analysis folder and its subdirectories
mkdir -p "$ANALYSIS_FOLDER"
mkdir -p "$ANALYSIS_FOLDER/.nextflow"
mkdir -p "$ANALYSIS_FOLDER/Logs_Intermediates"
mkdir -p "$ANALYSIS_FOLDER/Results"
mkdir -p "$ANALYSIS_FOLDER/errors"
mkdir -p "$ANALYSIS_FOLDER/work"

# Create files with content
echo "sample_id,sample_name,sample_type,panel,read1_fastq,read2_fastq" > "$ANALYSIS_FOLDER/SampleSheet.csv"
echo "[$(date)] Pipeline started\n[$(date)] Processing run folder: $RUN_FOLDER\n[$(date)] Analysis output: $ANALYSIS_FOLDER" > "$ANALYSIS_FOLDER/analysis.log"
echo "{\"runFolder\": \"$RUN_FOLDER\", \"analysisFolder\": \"$ANALYSIS_FOLDER\", \"pipeline_version\": \"1.0.0\"}" > "$ANALYSIS_FOLDER/inputs.json"
echo "Analysis completed successfully on $(date)" > "$ANALYSIS_FOLDER/receipt"

# Set appropriate permissions (similar to those in the screenshot)
chmod 755 "$ANALYSIS_FOLDER"
chmod 755 "$ANALYSIS_FOLDER/.nextflow" "$ANALYSIS_FOLDER/Logs_Intermediates" "$ANALYSIS_FOLDER/Results" "$ANALYSIS_FOLDER/errors" "$ANALYSIS_FOLDER/work"
chmod 644 "$ANALYSIS_FOLDER/SampleSheet.csv" "$ANALYSIS_FOLDER/analysis.log" "$ANALYSIS_FOLDER/inputs.json" "$ANALYSIS_FOLDER/receipt"

echo "Analysis folder structure created at $ANALYSIS_FOLDER"