import argparse
from pathlib import Path
import re
from datetime import datetime
from shutil import copytree as sh_copytree
from subprocess import run as subp_run



def main():
    parser = argparse.ArgumentParser(description="Process sample subset from arrival directory.")

    parser.add_argument(
        "--run_dir",
        type=str,
        required=True,
        help="Path to the run/sample directory"
    )

    parser.add_argument(
        "--sample_ids",
        type=str,
        required=True,
        help="Path to the run/sample directory"
    )

    parser.add_argument(
        "--input_type",
        type=str,
        required=True,
        help="Path to the run/sample directory"
    )

    args = parser.parse_args()

    run_dir = Path(args.run_dir)

    input_type = str(args.input_type)
    if input_type == 'samples':
        input_dir = run_dir / 'Analysis/1/Data/BCLConvert/fastq'

    sample_ids = str(args.sample_ids)
    sample_list = [s.strip() for s in sample_ids.split(',')]
    flowcell_name = run_dir.name
    input_staging_dir = Path('/staging/tmp') / flowcell_name
    run_name = f"{datetime.today().strftime('%y%m%d')}_TSO_Onco"
    analysis_dir = input_staging_dir / run_name
    sample_sheet = run_dir / 'SampleSheet_Analysis.csv'
    results_dir = Path('/mnt/NovaseqXplus/07_Oncoservice/Analyseergebnisse') / run_name
    dragen_script = Path('/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh')

    print(f"Staging the run {run_name}.")
    input_staging_dir.mkdir(parents=True, exist_ok=True)
    for sample_id in sample_list:
        matching_dirs = list(input_dir.glob(f'*{sample_id}*'))
        for src_dir in matching_dirs:
            dst_dir = input_staging_dir / src_dir.name
            if src_dir.is_dir():
                sh_copytree(src_dir, dst_dir, dirs_exist_ok=True)

    print(f"Staging completed! Running the TSO500 script for the run {run_name}.")

    dragen_call = f'{str(dragen_script)} --fastqFolder {str(input_staging_dir)}  --sampleSheet {str(sample_sheet)} --sampleIDs {str(sample_ids)} --analysisFolder {str(analysis_dir)}'
    subp_run(dragen_call, check=True, shell=True)

    print(f"TSO500 script completed! Transferring results for the run {run_name}.")
    sh_copytree(analysis_dir, results_dir)

    print(f"Transfer completed! The run {run_name} was succesfully processed")


if __name__ == "__main__":
    main()
