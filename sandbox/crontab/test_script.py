import subprocess
from datetime import datetime

log_file = "/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/sandbox/crontab/log.txt"  # change to your desired location

cmd = '/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh -h'
try:
    result = subprocess.run(
        cmd,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # Append successful output too if needed
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - Command succeeded\n")
        f.write(result.stdout + "\n")
except subprocess.CalledProcessError as e:
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - The command had failed: {e}\n")
        f.write("STDOUT:\n" + e.stdout + "\n")
        f.write("STDERR:\n" + e.stderr + "\n")
