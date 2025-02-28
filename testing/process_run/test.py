import subprocess

process_call = ['snakemake', '-j1', '-s', '/mnt/Novaseq/TSO_pipeline/02_Development/testing/process_run/test']
try:
    subprocess.run(process_call).check_returncode()
except subprocess.CalledProcessError as e:
    message = f"Process failed with a return code: {e.returncode}."
    raise RuntimeError(message)

print('Ze process has run succesfulliah')