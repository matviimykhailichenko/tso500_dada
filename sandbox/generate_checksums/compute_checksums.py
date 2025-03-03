# Imports
from subprocess import run as subp_run, CalledProcessError

compute_checksums_call = f"rsync -rl --checksum --checksum-choice=md5 --out-format=\"%C %n\" /home/matvii/PycharmProjects/TSO_500_DRAGEN_pipeline/sandbox/generate_checksums/source/ /home/matvii/PycharmProjects/TSO_500_DRAGEN_pipeline/sandbox/generate_checksums/destination > /home/matvii/PycharmProjects/TSO_500_DRAGEN_pipeline/sandbox/generate_checksums/checksum_file_path.txt"
try:
    subp_run(compute_checksums_call, shell=True).check_returncode()
except CalledProcessError as e:
    message = f"Transfering results had failed with return a code {e.returncode}. Error output: {e.stderr}"
    print(message)
    # delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
    # delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
    # delete_directory(dead_dir_path=results_dir_path,logger_runtime=logger)
    raise RuntimeError(message)