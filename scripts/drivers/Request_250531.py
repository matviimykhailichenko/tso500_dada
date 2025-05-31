from pathlib import Path
import shutil
import subprocess
from datetime import datetime

# Paths
source_dir = Path('/mnt/NovaseqXplus/02_HuGe_Forschung/Runs/20250528_LH00803_0010_B22KVHWLT4/Analysis/1/Data/BCLConvert/fastq')
run_name = source_dir.parents[4].name
staging_base = Path('/staging/tmp')
staging_run_dir = staging_base / '20250528_LH00803_0010_B22KVHWLT4' / 'fastq'
samplesheet = staging_base / '20250528_LH00803_0010_B22KVHWLT4' / 'SampleSheet.csv'

# Generate analysis folder name based on current date
today_str = datetime.today().strftime('%y%m%d')
analysis_folder_name = f'{today_str}_TSO_Oncoservice'
analysis_run_dir = staging_base / analysis_folder_name

# Final destination for analysis results
analysis_dest_dir = Path('/mnt/NovaseqXplus/07_Oncoservice/Analyseergebnisse')


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
