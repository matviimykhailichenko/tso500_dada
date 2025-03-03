# Imports
from subprocess import run as subp_run, CalledProcessError


rsync_call = [str('/usr/bin/rsync'), '-rl', '--checksum',
                      str('/staging/test_run_Oncoservice/'), str('/mnt/Novaseq/07_Oncoservice/Analyseergebnisse/test_run_Oncoservice')]
try:
    subp_run(rsync_call).check_returncode()
except CalledProcessError as e:
    message = f"Transfering results had failed with return a code {e.returncode}. Error output: {e.stderr}"
    print(message)
    # delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
    # delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
    # delete_directory(dead_dir_path=results_dir_path,logger_runtime=logger)
    raise RuntimeError(message)