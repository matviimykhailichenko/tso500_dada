#!/bin/bash

set -e  # exit as soon as a command fails

# ACTIVATE 'TSO500ichorCNA' CONDA ENVIRONMENT!
# EXECUTE FROM sy096!
# MUST NOT BE EXECUTED WITH SLURM! -> this changes the current working directory which messes with the code

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--indir)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --indir requires a non-empty argument."
                exit 1
            fi
            input_path="$2"
            shift 2
            ;;
        -p|--ichorpath)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --ichorpath requires a non-empty argument."
                exit 1
            fi
            path_to_ichor="$2"
            shift 2  # past argument and past value
            ;;
        -h|--help)
            echo "Usage: $0 --indir input --ichorpath path_to_ichor_folder"
            exit 0
            ;;
        *)
            # default commands
            echo "Unknown parameter passed: $1"
            exit 1
            ;;
    esac
    # shift  # DEACTIVATED because:
    #        For flags that take an argument, you need to shift twice — once for the flag itself,
    #        once for its argument. Your script shifts only once inside the case and once outside,
    #        which is correct if and only if the argument exists and is in $2. But if $2 is missing
    #        (i.e., the flag is the last argument or missing its value), your script will silently
    #        assign an empty value or even crash. It’s safer to check if the argument exists and shift
    #        correctly.
done

# check if parameters are available
if [[ -z "$input_path" || -z "$path_to_ichor" ]]; then
    echo "❌ Error: --indir and --ichorpath are required."  # e.g., /home/gpfs/o_spiegl/installations/ichorCNA
    echo "Usage: $0 -d/--indir <file> -p/--ichorpath <file>"
    exit 1
fi

echo "Input directory containing sample BAM files and bai index files inside: $input_path"
echo "Output directory where results will be moved to sample-by-sample: $path_to_ichor"

script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"  # WARNING - this does not work if called with SLURM!
path_hmm="/usr/bin"
# Raul's reference genome was not available

# RUN THE THANG!
# (analysis of everything with BAM in its name from input directory; sample-by-sample)
srun --nodelist=sy096 bash "${script_path}"/From_SortedBam_2_PDFs_CustomPoN-TS0500-10samples_1Mb_hg19_shared-folder.sh -idir "$input_path" -phmm $path_hmm -pichor "$path_to_ichor" &> "$input_path"/TSO500_liquid_offtarget_ichorCNA.log
