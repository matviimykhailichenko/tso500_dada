from pathlib import Path
from logging import getLogger, basicConfig, INFO, Logger
from subprocess import run as subp_run, CalledProcessError
from shutil import copytree as sh_copytree


# Assume this function is defined elsewhere or imported
def transfer_results_cbmed(paths: dict, input_type: str, logger: Logger, testing: bool = False):
    cbmed_results_dir: Path = paths['cbmed_results_dir']
    flowcell: str = paths['flowcell']
    flowcell_cbmed_dir: Path = cbmed_results_dir / 'flowcells' / flowcell
    data_cbmed_dir: Path = flowcell_cbmed_dir / flowcell
    dragen_cbmed_dir: Path = cbmed_results_dir / 'dragen'
    run_name: str = paths['run_name']
    cbmed_seq_dir: Path = paths['cbmed_seq_dir']
    rsync_path: str = paths['rsync_path']
    staging_temp_dir: Path = paths['staging_temp_dir']

    if input_type == 'sample':
        flowcell_run_dir: Path = cbmed_seq_dir / flowcell
        fastq_gen_seq_dir: Path = flowcell_run_dir / 'FastqGeneration'
    elif input_type == 'run':
        flowcell_run_dir: Path = cbmed_seq_dir / flowcell
        fastq_gen_seq_dir: Path = staging_temp_dir/ run_name / 'Logs_Intermediates' / 'FastqGeneration'

    results_staging: Path = staging_temp_dir / run_name
    results_cbmed_dir: Path = dragen_cbmed_dir / flowcell / 'Results'
    fastq_gen_results_dir: Path = flowcell_cbmed_dir / 'FastqGeneration'

    flowcell_cbmed_dir.mkdir(parents=True, exist_ok=True)
    results_cbmed_dir.mkdir(parents=True, exist_ok=True)

    if input_type == 'run':
        checksums_humgen = flowcell_cbmed_dir / f'{flowcell}_fastqs_HumGenNAS.sha256'
        checksums_call = (
            f'cd {str(fastq_gen_seq_dir)} && '
            "find . -type f -print0 | parallel -0 -j 40 sha256sum > "
            f"{str(checksums_humgen)}"
        )
        try:
            subp_run(checksums_call, shell=True).check_returncode()
        except CalledProcessError as e:
            message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
            print(message)
            logger.error(message)
            # raise RuntimeError(message)

    checksums_humgen = dragen_cbmed_dir / flowcell / f'{flowcell}_Results_HumGenNAS.sha256'
    checksums_call = (
        f'cd {str(results_staging)} && '
        "find . -type f -print0 | parallel -0 -j 40 sha256sum > "
        f"{str(checksums_humgen)}"
    )
    try:
        subp_run(checksums_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        print(message)
        logger.error(message)
        # raise RuntimeError(message)

    if not fastq_gen_results_dir.exists() or not any(fastq_gen_results_dir.iterdir()):
        sh_copytree(fastq_gen_seq_dir, fastq_gen_results_dir)

    if input_type == 'sample' and (not data_cbmed_dir.exists() or not any(data_cbmed_dir.iterdir())):
        rsync_call = (f"{rsync_path} -r "
                      f"{str(flowcell_run_dir)}/ "
                      f"{str(flowcell_cbmed_dir / flowcell)}")
        try:
            subp_run(rsync_call, shell=True, check=True)
        except CalledProcessError as e:
            message = f"Transferring results had FAILED: {e}"
            print(message)
            logger.error(message)
            # raise RuntimeError(message)

    elif input_type == 'run':
        rsync_call = (f"{rsync_path} -r "
                      f"{str(paths['run_dir'] / flowcell)}/ "
                      f"{str(data_cbmed_dir)}")
        try:
            subp_run(rsync_call, shell=True, check=True)
        except CalledProcessError as e:
            message = f"Transferring results had FAILED: {e}"
            print(message)
            logger.error(message)
            # raise RuntimeError(message)

    if input_type == 'run':
        log_file_path = flowcell_cbmed_dir / 'CBmed_copylog.log'
        rsync_call = (f"{rsync_path} -r "
                      f"--out-format=\"%C %n\" "
                      f"--log-file {str(log_file_path)} "
                      f"{str(fastq_gen_seq_dir)}/ "
                      f"{str(fastq_gen_results_dir)}")
        try:
            subp_run(rsync_call, shell=True, check=True)
        except CalledProcessError as e:
            message = f"Transferring results had FAILED: {e}"
            print(message)
            logger.error(message)
            # raise RuntimeError(message)

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
        print(message)
        logger.error(message)
        # raise RuntimeError(message)

    checksums_cbmed = flowcell_cbmed_dir / f'{flowcell}_fastqs.sha256'
    checksums_call = (
        f'cd {str(fastq_gen_results_dir)} && '
        "find . -type f -print0 | parallel -0 -j 40 sha256sum > "
        f"{str(checksums_cbmed)}"
    )
    try:
        subp_run(checksums_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        print(message)
        logger.error(message)
        # raise RuntimeError(message)

    checksums_cbmed = dragen_cbmed_dir / flowcell / f'{flowcell}_Results.sha256'
    checksums_call = (
        f'cd {str(results_cbmed_dir)} && '
        "find . -type f -print0 | parallel -0 -j 40 sha256sum > "
        f"{str(checksums_cbmed)}"
    )
    try:
        subp_run(checksums_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        print(message)
        logger.error(message)
        # raise RuntimeError(message)

    diff_call = (
        f'diff <(sort {str(checksums_humgen)}) <(sort {str(checksums_cbmed)})'
    )
    try:
        stdout = subp_run(diff_call, shell=True, capture_output=True,text=True, check=True, executable='/bin/bash').stdout.strip()
        if stdout is not None:
            message = f"Checksums in a CBmed run are different"
            # raise RuntimeError(message)
    except CalledProcessError as e:
        message = f"Computing diff for a CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        print(message)
        logger.error(message)
        # raise RuntimeError(message)


    if input_type == 'run':
        diff_call = (
            f'diff <(sort {str(fastq_gen_seq_dir)}) <(sort {str(fastq_gen_results_dir)})'
        )
        try:
            stdout = subp_run(diff_call, shell=True, capture_output=True, text=True, check=True,
                              executable='/bin/bash').stdout.strip()
            if stdout is not None:
                message = f"Checksums in a CBmed run are different"
                # raise RuntimeError(message)
        except CalledProcessError as e:
            message = f"Computing diff for a CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
            print(message)
            logger.error(message)
            # raise RuntimeError(message)

    return 0
# --- Setup logger ---
basicConfig(level=INFO)
logger = getLogger("''cbmed_transfer''")

# --- Setup parameters ---
input_type = 'run'

paths = {
    'run_dir': Path('/mnt/CBmed_NAS3/Genomics/TSO500_liquid/250718_BI_735_batch3'),
    'staging_temp_dir': Path('/staging/tmp'),
    'cbmed_results_dir': Path('/mnt/CBmed_NAS3/Genomics/TSO500_liquid'),
    'flowcell': '250718_A01664_0532_BHHMK5DSXF',
    'run_name': '250718_BI_735_batch3',
    'cbmed_seq_dir': Path('/mnt/CBmed_NAS3/Genomics/TSO500_liquid'),
    'rsync_path': '/usr/bin/rsync'}

# --- Run transfer ---
if __name__ == "__main__":
    try:
        result_code = transfer_results_cbmed(paths=paths, input_type=input_type, logger=logger)
        print(f"Transfer completed with result: {result_code}")
    except Exception as e:
        print(f"Transfer failed: {str(e)}")
