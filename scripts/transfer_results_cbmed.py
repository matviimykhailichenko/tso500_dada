from pathlib import Path
from logging import getLogger, basicConfig, INFO

# Assume this function is defined elsewhere or imported
def transfer_results_cbmed(paths: dict, input_type: str, logger: Logger, testing: bool = False):
    data_staging: Path = paths[f'{input_type}_staging_temp_dir']
    cbmed_results_dir: Path = paths['cbmed_results_dir']
    flowcell: str = paths['flowcell']
    flowcell_cbmed_dir: Path = cbmed_results_dir / 'flowcells' / flowcell
    data_cbmed_dir: Path = flowcell_cbmed_dir / flowcell
    dragen_cbmed_dir: Path = cbmed_results_dir / 'dragen'
    run_name: str = paths['run_name']
    cbmed_seq_dir: Path = paths['cbmed_seq_dir']
    run_seq_dir: Path = cbmed_seq_dir / paths['run_name']
    rsync_path: str = paths['rsync_path']
    staging_temp_dir: Path = paths['staging_temp_dir']

    if input_type == 'sample':
        flowcell_run_dir: Path = cbmed_seq_dir / flowcell
    elif input_type == 'run':
        flowcell_run_dir: Path = cbmed_seq_dir / flowcell

    results_staging: Path = staging_temp_dir / run_name
    results_cbmed_dir: Path = dragen_cbmed_dir / flowcell / 'Results'
    samplesheet_results_dir: Path = results_staging / 'SampleSheet.csv'
    samplesheet_cbmed_dir: Path = dragen_cbmed_dir/ flowcell / 'SampleSheet.csv'
    if input_type == 'sample':
        fastq_gen_seq_dir: Path = run_seq_dir / 'FastqGeneration'
        fastq_gen_results_dir: Path = results_cbmed_dir / 'FastqGeneration'
    elif input_type == 'run':
        fastq_gen_seq_dir: Path = results_staging / 'Logs_Intermediates' / 'FastqGeneration'
        fastq_gen_results_dir: Path = results_cbmed_dir / 'FastqGeneration'

    data_cbmed_dir.mkdir(parents=True, exist_ok=True)
    results_cbmed_dir.mkdir(parents=True, exist_ok=True)

    # TODO Compute checksums for data and results on /staging/

    if not data_cbmed_dir.exists() or data_cbmed_dir.stat().st_size == 0:
        checksums_data_humgen = flowcell_cbmed_dir / f'{flowcell}_HumGenNAS.sha256'
        checksums_call = (r'find '
                          f'{str(data_staging)} '
                          r'-type f -exec sha256sum {} \; | tee  '
                          f'{str(checksums_data_humgen)}')
        try:
            subp_run(checksums_call, shell=True).check_returncode()
        except CalledProcessError as e:
            message = (f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. "
                       f"Error output: {e.stderr}")
            notify_bot(message)
            logger.error(message)
            raise RuntimeError(message)

    checksums_humgen = dragen_cbmed_dir / flowcell / f'{flowcell}_Results_HumGenNAS.sha256'
    checksums_call = (r'find '
                      f'{str(results_staging)} '
                      r'-type f -exec sha256sum {} \; | tee  '
                      f'{str(checksums_humgen)}')
    try:
        subp_run(checksums_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        notify_bot(message)
        logger.error(message)
        raise RuntimeError(message)

    # TODO Supposed to append existing checksums
    if input_type == 'sample':
        checksums_raw_data = flowcell_cbmed_dir / f'{flowcell}_HumGenNAS.sha256'
        checksums_call = (r'find '
                          f'{str(run_seq_dir)} '
                          r'-type f -exec sha256sum {} \; | tee  '
                          f'{str(checksums_raw_data)}')
        try:
            subp_run(checksums_call, shell=True).check_returncode()
        except CalledProcessError as e:
            message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
            notify_bot(message)
            logger.error(message)
            raise RuntimeError(message)

    # TODO Transfer results and data
    # TODO Compare checksums

    if input_type == 'sample' and (not data_cbmed_dir.exists() or data_cbmed_dir.stat().st_size) == 0:
        log_file_path = flowcell_cbmed_dir / 'CBmed_copylog.log'
        rsync_call = (f"{rsync_path} -r "
                      f"--out-format=\"%C %n\" "
                      f"--log-file {str(log_file_path)} "
                      f"--exclude='FastqGeneration' "
                      f"{str(flowcell_run_dir)}/ "
                      f"{str(data_cbmed_dir)}")
        try:
            subp_run(rsync_call, shell=True).check_returncode()
        except CalledProcessError as e:
            message = f"Transferring results had FAILED: {e}"
            notify_bot(message)
            logger.error(message)
            raise RuntimeError(message)

    elif input_type == 'run':
        log_file_path = flowcell_cbmed_dir / 'CBmed_copylog.log'
        rsync_call = (f"{rsync_path} -r "
                      f"--out-format=\"%C %n\" "
                      f"--log-file {str(log_file_path)} "
                      f"{str(paths['run_dir'])}/ "
                      f"{str(data_cbmed_dir)}")
        try:
            subp_run(rsync_call, shell=True).check_returncode()
        except CalledProcessError as e:
            message = f"Transferring results had FAILED: {e}"
            notify_bot(message)
            logger.error(message)
            raise RuntimeError(message)

    if not fastq_gen_results_dir.exists() or fastq_gen_results_dir.stat().st_size == 0:
        log_file_path = results_cbmed_dir.parent / 'CBmed_copylog.log'
        rsync_call = (f"{rsync_path} -r "
                      f"--out-format=\"%C %n\" "
                      f"--log-file {str(log_file_path)} "
                      f"{str(fastq_gen_seq_dir)}/ "
                      f"{str(fastq_gen_results_dir)}")
        try:
            subp_run(rsync_call, shell=True).check_returncode()
        except CalledProcessError as e:
            message = f"Transferring results had FAILED: {e}"
            notify_bot(message)
            logger.error(message)
            raise RuntimeError(message)

    log_file_path = results_cbmed_dir.parent / 'CBmed_copylog.log'
    rsync_call = (f"{rsync_path} -r "
                  f"--out-format=\"%C %n\" "
                  f"--log-file {str(log_file_path)} "
                  f"{str(results_staging)}/ "
                  f"{str(results_cbmed_dir)}")
    try:
        subp_run(rsync_call,shell=True,check=True)
    except CalledProcessError as e:
        message = f"Transferring results had FAILED: {e}"
        notify_bot(message)
        logger.error(message)
        raise RuntimeError(message)

    if not samplesheet_cbmed_dir.exists() or samplesheet_cbmed_dir.stat().st_size == 0:
        rsync_call = (f"{rsync_path} "
                      f"{str(samplesheet_results_dir)} "
                      f"{str(samplesheet_cbmed_dir)}")
        try:
            subp_run(rsync_call,shell=True,check=True)
        except CalledProcessError as e:
            message = f"Transferring results had FAILED: {e}"
            notify_bot(message)
            logger.error(message)
            raise RuntimeError(message)

    # TODO Make checksums for files data/results on CBmed NAS
    checksums_data_cbmed = flowcell_cbmed_dir / f'{flowcell}.sha256'
    checksums_call = (r'find '
                      f'{str(data_cbmed_dir)} '
                      r'-type f -exec sha256sum {} \; | tee  '
                      f'{str(checksums_data_cbmed)}')
    try:
        subp_run(checksums_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = (f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. "
                   f"Error output: {e.stderr}")
        notify_bot(message)
        logger.error(message)
        raise RuntimeError(message)

    checksums_results_cbmed = dragen_cbmed_dir / flowcell / f'{flowcell}_Results.sha256'
    checksums_call = (r'find '
                      f'{str(results_cbmed_dir)} '
                      r'-type f -exec sha256sum {} \; | tee  '
                      f'{str(checksums_results_cbmed)}')
    try:
        subp_run(checksums_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        notify_bot(message)
        logger.error(message)
        raise RuntimeError(message)

    # TODO Compare checksums

    return 0
# --- Setup logger ---
basicConfig(level=INFO)
logger = getLogger("''cbmed_transfer''")

# --- Setup parameters ---
input_type = 'run'

paths = {
    'run_dir': Path('/mnt/CBmed_NAS3/Genomics/TSO500_liquid/250620_BI_739_batch1'),
    'staging_temp_dir': Path('/staging/tmp'),
    'cbmed_results_dir': Path('/mnt/CBmed_NAS3/Genomics/TSO500_liquid'),
    'flowcell': '250620_A01664_0523_AHCMHMDSXF',
    'run_name': '250620_BI_739_batch1',
    'cbmed_seq_dir': Path('/mnt/CBmed_NAS3/Genomics/TSO500_liquid'),
    'rsync_path': '/usr/bin/rsync',
    'run_staging_temp_dir': Path('/staging/tmp'),  # optional alias if needed
    'sample_staging_temp_dir': Path('/staging/tmp'),  # included to avoid key errors inside function
}

# --- Run transfer ---
if __name__ == "__main__":
    try:
        result_code = transfer_results_cbmed(paths=paths, input_type=input_type, logger=logger)
        print(f"Transfer completed with result: {result_code}")
    except Exception as e:
        print(f"Transfer failed: {str(e)}")
