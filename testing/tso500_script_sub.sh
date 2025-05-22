#!/bin/bash

# Default values
RUN_FOLDER=""
ANALYSIS_FOLDER=""
FASTQ_FOLDER=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --runFolder)
      RUN_FOLDER="$2"
      shift 2
      ;;
    --fastqFolder)
      FASTQ_FOLDER="$2"
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

# Determine active input folder
INPUT_FOLDER="${RUN_FOLDER:-$FASTQ_FOLDER}"

# Check if required parameters are provided
if [ -z "$INPUT_FOLDER" ] || [ -z "$ANALYSIS_FOLDER" ]; then
  echo "Usage: $0 (--runFolder <run_folder_path> | --fastqFolder <fastq_folder_path>) --analysisFolder <analysis_folder_path>"
  exit 1
fi

# Create the analysis folder and its subdirectories
mkdir -p "$ANALYSIS_FOLDER"
mkdir -p "$ANALYSIS_FOLDER/.nextflow"
mkdir -p "$ANALYSIS_FOLDER/Logs_Intermediates"
mkdir -p "$ANALYSIS_FOLDER/Results"
mkdir -p "$ANALYSIS_FOLDER/errors"
mkdir -p "$ANALYSIS_FOLDER/work"

# Handle specific logic for fastqFolder or runFolder
if [ -n "$FASTQ_FOLDER" ]; then
  # Get base name of FASTQ folder
  BASE_NAME=$(basename "$FASTQ_FOLDER")
  mkdir -p "$ANALYSIS_FOLDER/Results/$BASE_NAME"

elif [ -n "$RUN_FOLDER" ]; then
  mkdir -p "$ANALYSIS_FOLDER/Results/Sample1"
  mkdir -p "$ANALYSIS_FOLDER/Results/Sample2"
  mkdir -p "$ANALYSIS_FOLDER/Results/Sample3"
  mkdir -p "$ANALYSIS_FOLDER/Logs_Intermediates/FastqGeneration/Sample1"
  mkdir -p "$ANALYSIS_FOLDER/Logs_Intermediates/FastqGeneration/Sample2"
  mkdir -p "$ANALYSIS_FOLDER/Logs_Intermediates/FastqGeneration/Sample3"
fi

# Create files with content
echo "sample_id,sample_name,sample_type,panel,read1_fastq,read2_fastq" > "$ANALYSIS_FOLDER/SampleSheet.csv"
{
  echo "[$(date)] Pipeline started"
  echo "[$(date)] Processing input folder: $INPUT_FOLDER"
  echo "[$(date)] Analysis output: $ANALYSIS_FOLDER"
} > "$ANALYSIS_FOLDER/analysis.log"
echo "{\"inputFolder\": \"$INPUT_FOLDER\", \"analysisFolder\": \"$ANALYSIS_FOLDER\", \"pipeline_version\": \"1.0.0\"}" > "$ANALYSIS_FOLDER/inputs.json"
echo "Analysis completed successfully on $(date)" > "$ANALYSIS_FOLDER/receipt"

# Set appropriate permissions
chmod 755 "$ANALYSIS_FOLDER"
chmod 755 "$ANALYSIS_FOLDER/.nextflow" "$ANALYSIS_FOLDER/Logs_Intermediates" "$ANALYSIS_FOLDER/Results" "$ANALYSIS_FOLDER/errors" "$ANALYSIS_FOLDER/work"
chmod 644 "$ANALYSIS_FOLDER/SampleSheet.csv" "$ANALYSIS_FOLDER/analysis.log" "$ANALYSIS_FOLDER/inputs.json" "$ANALYSIS_FOLDER/receipt"

echo "Analysis folder structure created at $ANALYSIS_FOLDER"
