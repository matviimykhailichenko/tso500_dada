import argparse
from pathlib import Path
import re
import datetime
from shutil import copytree as sh_copytree
from ..logging_ops import notify_bot
from subprocess import run as subp_run



def main():
    parser = argparse.ArgumentParser(description="Process sample subset from arrival directory.")

    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Path to the run/sample directory"
    )

    args = parser.parse_args()

    run_dir = Path(args.input_dir)
    flowcell_name = run_dir.name
    run_staging_dir = Path('/staging/tmp') / flowcell_name
    run_name = f"{datetime.today().strftime('%y%m%d')}_TSO_Onco"
    analysis_dir = run_staging_dir / run_name
    sample_sheet = run_dir / 'SampleSheet_Analysis.csv'
    results_dir = Path('/mnt/NovaseqXplus/07_Oncoservice/Analyseergebnisse') / run_name
    dragen_script = Path('/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh')

    notify_bot(f"Staging the run {run_name}.")
    sh_copytree(run_dir, run_staging_dir)

    notify_bot(f"Staging completed! Running the TSO500 script for the run {run_name}.")
    dragen_call = f'{str(dragen_script)} --runFolder {str(run_staging_dir)} --analysisFolder {str(analysis_dir)} --sampleSheet {str(sample_sheet)}'
    subp_run(dragen_call, check=True, shell=True)

    notify_bot(f"TSO500 script completed! Transferring results for the run {run_name}.")
    sh_copytree(analysis_dir, results_dir)

    notify_bot(f"Transfer completed! The run {run_name} was succesfully processed")


if __name__ == "__main__":
    main()
