from pathlib import Path
from logging import getLogger, basicConfig, INFO

# Assume this function is defined elsewhere or imported
from helpers import transfer_results_cbmed  # <-- replace with actual import or paste the function in this script

# --- Setup logger ---
basicConfig(level=INFO)
logger = getLogger("cbmed_transfer")

# --- Setup parameters ---
input_type = 'run'

paths = {
    'run_dir': Path('/mnt/CBmed_NAS3/Genomics/TSO500_liquid/250620_BI_739_batch1'),
    'staging_temp_dir': Path('/staging/tmp'),
    'cbmed_results_dir': Path('/mnt/CBmed_NAS3/Genomics/TSO500_liquid'),
    'flowcell': '250620_A01664_0523_AHCMHMDSXF',
    'run_name': '250620_BI_739_batch1',
    'cbmed_seq_dir': Path('/mnt/CBmed_NAS3/Genomics/TSO500_liquid'),
    'rsync_path': '/usr/bin/rsync',
    'run_staging_temp_dir': Path('/staging/tmp'),  # optional alias if needed
    'sample_staging_temp_dir': Path('/staging/tmp'),  # included to avoid key errors inside function
}

# --- Run transfer ---
if __name__ == "__main__":
    try:
        result_code = transfer_results_cbmed(paths=paths, input_type=input_type, logger=logger)
        print(f"Transfer completed with result: {result_code}")
    except Exception as e:
        print(f"Transfer failed: {str(e)}")
