import argparse
from pathlib import Path
from datetime import datetime
from shutil import copy as sh_copy, copytree as sh_copytree, copy2 as sh_copy
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
        required=False,
        help="Path to the run/sample directory"
    )

    parser.add_argument(
        "--input_type",
        type=str,
        required=True,
        help="Type of the input: run/sample"
    )

    parser.add_argument(
        "--tag",
        type=str,
        required=True,
        help="Tag of the input"
    )

    args = parser.parse_args()

    run_dir = Path(args.run_dir)

    input_type = str(args.input_type)
    tag = str(args.tag)
    dragen_script = Path('/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh')
    flowcell_name = run_dir.name
    staging_dir = Path('/staging/tmp')
    input_staging_dir = staging_dir / flowcell_name
    date = flowcell_name.split('_')[0]  # '20250613'
    formatted_date = date[2:8]  # '250613'
    run_name = f"{formatted_date}_TSO500Onco"
    analysis_dir = staging_dir / run_name
    if input_type == 'sample':
        input_dir = run_dir / 'Analysis/2/Data/BCLConvert/fastq'
        sample_ids = str(args.sample_ids)
        sample_list = [s.strip() for s in sample_ids.split(',')]
        sample_sheet = run_dir / 'SampleSheet_Analysis.csv'
        dragen_call = f'{str(dragen_script)} --fastqFolder {str(input_staging_dir)}  --sampleSheet {str(sample_sheet)} --sampleIDs {str(sample_ids)} --analysisFolder {str(analysis_dir)}'
    elif input_type == 'run':
        sample_sheet = run_dir / 'SampleSheet.csv'
        dragen_call = f'{str(dragen_script)} --runFolder {str(input_staging_dir)}  --sampleSheet {str(sample_sheet)} --analysisFolder {str(analysis_dir)}'
    if tag == 'CBM':
        results_dir = Path('/mnt/CBmed_NAS3/Genomics/TSO500_liquid/dragen') / flowcell_name / flowcell_name
    elif tag == 'ONC':
        results_dir = Path('/mnt/NovaseqXplus/01_HuGe_Diagnostik/Analyseergebnisse') / run_name

    print(f"Staging the run {run_name}.")

    if input_type == 'sample':
        input_staging_dir.mkdir(parents=True, exist_ok=True)
        for sample_id in sample_list:
            for fastq_file in input_dir.glob(f'{sample_id}_*.fastq.gz'):
                dst_file = input_staging_dir / fastq_file.name
                sh_copy(fastq_file, dst_file)
    elif input_type == 'run':
        rsync_call = f'rsync -ra "{run_dir}/" "{input_staging_dir}/"'
        subp_run(rsync_call, check=True, shell=True)
        sh_copytree(str(run_dir), input_staging_dir)
    print(f"Staging completed! Running the TSO500 script for the run {run_name}.")

    subp_run(dragen_call, check=True, shell=True)

    print(f"TSO500 script completed! Transferring results for the run {run_name}.")

    rsync_call = f'rsync -av --exclude=".nextflow" --exclude "work" {analysis_dir} {results_dir}/'
    subp_run(rsync_call, check=True, shell=True)

    print(f"Transfer completed! The run {run_name} was succesfully processed")


if __name__ == "__main__":
    main()
