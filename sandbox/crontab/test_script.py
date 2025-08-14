import subprocess
from datetime import datetime

log_file = "/path/to/error_log.txt"  # change to your desired location

cmd = '/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh -h'

try:
    result = subprocess.run(
        cmd,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True  # Python 3.6 compatible
    )
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - Command succeeded\n")
        f.write(result.stdout + "\n")
except subprocess.CalledProcessError as e:
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - The command had failed: {e}\n")
        f.write("STDOUT:\n" + (e.output or "") + "\n")
        f.write("STDERR:\n" + (e.stderr or "") + "\n")
