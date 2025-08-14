import subprocess
from datetime import datetime

log_file = "/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/sandbox/crontab/error_log.txt"  # change to your desired location

cmd = '/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh -h'
try:
    subprocess.run(cmd, shell=True, check=True)
except Exception as e:
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - The command had failed: {e}\n")
