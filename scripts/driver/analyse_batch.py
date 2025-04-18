import argparse
from pathlib import Path



def main():
    parser = argparse.ArgumentParser(description="Process sample subset from arrival directory.")

    parser.add_argument(
        "--sample_subset",
        type=str,
        required=True,
        help="Comma-separated list of samples (e.g., s1,s2,s3)"
    )

    parser.add_argument(
        "--arrival_dir",
        type=str,
        required=True,
        help="Path to the run directory"
    )

    args = parser.parse_args()

    samples = args.sample_subset.split(",")

    staging_base = Path('/staging/tmp')
    staging_run_dir = staging_base / '20250410_LH00803_0007_A22L2JGLT4' / 'fastq'
    samplesheet = staging_base / '20250410_LH00803_0007_A22L2JGLT4' / 'SampleSheet.csv'

    # Generate analysis folder name based on current date
    today_str = datetime.today().strftime('%y%m%d')
    analysis_folder_name = f'{today_str}_TSO_Oncoservice'
    analysis_run_dir = staging_base / analysis_folder_name

    # Final destination for analysis results
    analysis_dest_dir = Path('/mnt/NovaseqXplus/07_Oncoservice/Analyseergebnisse')

    # Sample IDs (prefixes)
    sample_ids = [
        'C706_1', 'P636_3', 'P604_12_manuell', 'P743_1_manuell', 'B664_1_manuell',
        'B279_9_manuell', 'P740_1', 'O407_1'
    ]

    # Step 1: Create staging run directory if not exists
    staging_run_dir.mkdir(parents=True, exist_ok=True)

    # Step 2: Copy FASTQ files that do NOT match sample IDs
    for file_path in source_dir.glob('*'):
        if file_path.is_file() and not any(file_path.name.startswith(sample_id) for sample_id in sample_ids):
            dest_path = staging_run_dir / file_path.name
            print(f"Copying {file_path.name} to staging...")
            shutil.copy2(file_path, dest_path)

    # Step 3: Run DRAGEN pipeline
    dragen_script = Path('/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh')
    cmd = [
        str(dragen_script),
        '--fastqFolder', str(staging_run_dir),
        '--analysisFolder', str(analysis_run_dir),
        '--sampleSheet', str(samplesheet)
    ]

    print("Running DRAGEN pipeline...")
    subprocess.run(cmd, check=True)
    print("DRAGEN analysis complete.")

    # Step 4: Transfer analysis output to destination
    final_dest = analysis_dest_dir / analysis_folder_name
    print(f"Transferring analysis folder to {final_dest}...")
    shutil.copytree(analysis_run_dir, final_dest, dirs_exist_ok=True)
    print("Transfer complete.")


if __name__ == "__main__":
    main()
