# Imports
from subprocess import run as subp_run, CalledProcessError

compute_checksums_call = r'find /home/matvii/PycharmProjects/TSO_500_DRAGEN_pipeline/sandbox/generate_checksums/source/ -type f -exec sha256sum {} \; | tee  /home/matvii/PycharmProjects/TSO_500_DRAGEN_pipeline/sandbox/generate_checksums/source.sha256'
try:
    subp_run(compute_checksums_call, shell=True).check_returncode()
except CalledProcessError as e:
    message = f"Transfering results had failed with return a code {e.returncode}. Error output: {e.stderr}"
    print(message)
    # delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
    # delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
    # delete_directory(dead_dir_path=results_dir_path,logger_runtime=logger)
    raise RuntimeError(message)