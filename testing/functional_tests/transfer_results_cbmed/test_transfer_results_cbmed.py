from scripts.helpers import transfer_results_cbmed
from scripts.logging_ops import setup_logger

logger_runtime = setup_logger('transfer_results_cbmed',
                              '/mnt/Novaseq/TSO_pipeline/03_Production/testing/functional_tests/transfer_results_cbmed/last_execution.log')
try:
    transfer_results_cbmed(flowcell='test_run_files_dir',
                       rsync_path_str='/usr/bin/rsync',
                       run_name='test_results_dir',
                       logger=logger_runtime,
                       testing=True)
except Exception as e:
    print(e)