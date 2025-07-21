#!/usr/bin/env python3

import subprocess
import time
import os
import signal
import sys

# === CONFIG ===
ENV_ACTIVATE = "/staging/env/tso500_dragen_pipeline/bin/activate"
SCRIPT = "/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/processing.py"
LOGFILE = "/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/logs/crontab_last_execution.log"
PIDFILE = "/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/loop.pid"

# === Write PID ===
with open(PIDFILE, "w") as f:
    f.write(str(os.getpid()))
print(f"[INFO] Loop PID: {os.getpid()} (written to {PIDFILE})")

# === Loop forever ===
try:
    while True:
        print("[INFO] Running processing.py ...")

        # Compose the full shell command to run in bash with env activation
        cmd = f"source {ENV_ACTIVATE} && python3 {SCRIPT} >> {LOGFILE} 2>&1 && deactivate"

        subprocess.run(cmd, shell=True, executable="/bin/bash")

        print("[INFO] Sleeping 60s ...")
        time.sleep(60)

except KeyboardInterrupt:
    print("\n[INFO] Stopping loop due to keyboard interrupt.")
except Exception as e:
    print(f"[ERROR] {e}")
finally:
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)
    sys.exit(0)
