#!/bin/bash

# Base directory
BASE_DIR="/mnt/Novaseq/07_Oncoservice/Runs_TEST"

# Create parent run directory
RUN_DIR="${BASE_DIR}/250213_TSO500_Onco"
mkdir -p "${RUN_DIR}"

# Create sample directory
SAMPLE_DIR="${RUN_DIR}/250213_A01664_0452_AH2J5VDMX2"
mkdir -p "${SAMPLE_DIR}"

# Create MyRun directory
mkdir -p "${RUN_DIR}/MyRun"

# Create empty SampleSheet.csv
touch "${RUN_DIR}/SampleSheet.csv"

# Create subdirectories in sample directory
mkdir -p "${SAMPLE_DIR}/Config"
mkdir -p "${SAMPLE_DIR}/Data"
mkdir -p "${SAMPLE_DIR}/InterOp"
mkdir -p "${SAMPLE_DIR}/Logs"
mkdir -p "${SAMPLE_DIR}/Recipe"
mkdir -p "${SAMPLE_DIR}/Thumbnail_Images"

# Create empty files in sample directory
touch "${SAMPLE_DIR}/CopyComplete.txt"
touch "${SAMPLE_DIR}/RTA3.cfg"
touch "${SAMPLE_DIR}/RTAComplete.txt"
touch "${SAMPLE_DIR}/RunInfo.xml"
touch "${SAMPLE_DIR}/RunParameters.xml"
touch "${SAMPLE_DIR}/SequenceComplete.txt"

echo "Directory structure created in ${BASE_DIR}"