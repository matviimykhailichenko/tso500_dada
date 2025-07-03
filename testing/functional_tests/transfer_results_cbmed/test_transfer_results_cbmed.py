from scripts.helpers import transfer_results_cbmed, setup_paths
from scripts.logging_ops import setup_logger
from shutil import which as sh_which
from pathlib import Path
from datetime import datetime



paths = setup_paths(input_path='/mnt/CBmed_NAS3/Genomics/TSO500_liquid_TEST/test_run_cbmed_nsqx',
                    input_type='samples',
                    tag='CBM',
                    )

logger_runtime = setup_logger('transfer_results_cbmed',
                              '/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/transfer_results_cbmed/last_execution.log')
try:
    transfer_results_cbmed(paths=paths,
                           flowcell='test_run_files_dir',
                           input_type='samples',
                           logger=logger_runtime,
                           testing=True)

except Exception as e:
    print(e)