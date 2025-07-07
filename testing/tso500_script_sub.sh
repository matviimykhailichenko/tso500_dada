#!/bin/bash

# Default values
RUN_FOLDER=""
ANALYSIS_FOLDER=""
FASTQ_FOLDER=""
SAMPLE_IDS=()

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
    --sampleIDs)
      IFS=',' read -ra SAMPLE_IDS <<< "$2"
      shift 2
      ;;
    --sampleSheet)
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
  echo "Usage: $0 (--runFolder <run_folder_path> | --fastqFolder <fastq_folder_path>) --analysisFolder <analysis_folder_path> [--sampleIDs id1,id2,...]"
  exit 1
fi

# Check FASTQ files for provided sample IDs
if [ -n "$FASTQ_FOLDER" ] && [ ${#SAMPLE_IDS[@]} -gt 0 ]; then
  echo "Checking for FASTQ files matching sample IDs in $FASTQ_FOLDER..."
  for sample_id in "${SAMPLE_IDS[@]}"; do
    matches=$(find "$FASTQ_FOLDER" -type f -name "*${sample_id}*.fastq.gz")
    if [ -z "$matches" ]; then
      echo "Warning: No FASTQ files found for sample ID: $sample_id"
    else
      echo "Found FASTQ files for $sample_id:"
      echo "$matches"
    fi
  done
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
