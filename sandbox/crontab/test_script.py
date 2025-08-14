import subprocess

from scripts.logging_ops import notify_bot

cmd = '/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh -h'
try:
    subprocess.run(cmd, shell=True, check=True)
except Exception as e:
    notify_bot(f'The command had failed: {e}')