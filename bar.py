import subprocess


cmd = f"bash /media/matvii/30c92328-1f20-448d-a014-902558a05393/tso500_dragen_pipeline/sandbox/test.sh 2>&1 | tee -a test.log"
subprocess.run(cmd, check=True, shell=True)
