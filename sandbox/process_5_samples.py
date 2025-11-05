from subprocess import run


cmd = 'python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/scheduler.py -t'

for i in range(5):
    run(cmd, check=True, shell=True)
