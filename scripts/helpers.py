from pathlib import Path
from logging import Logger
from shutil import which as sh_which, rmtree as sh_rmtree, copy as sh_copy
from subprocess import Popen as subp_Popen, run as subp_run, PIPE as subp_PIPE, CalledProcessError
from typing import Optional
import yaml
from scripts.logging_ops import notify_bot, setup_logger, notify_pipeline_status
from datetime import datetime
import pandas as pd
from filelock import FileLock, Timeout




def is_server_available() -> bool:
    with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        server = get_server_ip()
        server_availability_dir = Path(config['server_availability_dir'])
        server_idle_tag = server_availability_dir / server / config['server_idle_tag']
        server_busy_tag = server_availability_dir / server / config['server_busy_tag']

    try:
        if Path(server_busy_tag).exists() and not Path(server_idle_tag).exists():
            return True
        return False
    except Exception as e:
        message = f"Failed to check server status: {e}"
        notify_bot(message)
        raise RuntimeError(message)


def delete_directory(dead_dir_path: Path, logger_runtime: Optional[Logger] = None):
    if dead_dir_path and dead_dir_path.is_dir():
        try:
            if logger_runtime:
                logger_runtime.info(f"deleting directory '{dead_dir_path}' ...")
            sh_rmtree(str(dead_dir_path))  # should also delete the directory itself along with its contents
            if logger_runtime:
                logger_runtime.info(f"successfully deleted directory '{dead_dir_path}'")
        except Exception as e:
            if logger_runtime:
                logger_runtime.warning(f"could not delete directory '{dead_dir_path}'. Error: {e}")
    else:
        if logger_runtime:
            logger_runtime.warning(f"could not delete directory '{dead_dir_path}': path does not exist")


def delete_file(dead_file_path: Path):
    if dead_file_path and dead_file_path.is_file():
        try:
            dead_file_path.unlink()
        except KeyboardInterrupt:
            return 255  # propagate KeyboardInterrupt outward
# TODO not sure if returning 255 is most logical


# TODO add check of the sx176 mountpoint
def is_nas_mounted(mountpoint_dir: str,
                   logger_runtime: Logger) -> bool:
    mountpoint_binary = sh_which('mountpoint')
    if not mountpoint_binary:
        mountpoint_binary = '/usr/bin/mountpoint'
        logger_runtime.warning(f"looked for the mountpoint executable at '{mountpoint_binary}' but didn't "
                               f"find the file (path was None) or could not access it (permission problem). "
                               f"Using the default one anyways at '{mountpoint_binary}'. This might cause "
                               f"subprocess failure!")
    ran_mount_check = subp_run([mountpoint_binary, mountpoint_dir], stdout=subp_PIPE, encoding='utf-8')
    try:
        ran_mount_check.check_returncode()
    except CalledProcessError:
        # TODO BOT!
        logger_runtime.error(f"the expected NAS mountpoint was not found at {mountpoint_dir}. Terminating..")
        return False

    if ran_mount_check.stdout.strip() != f'{mountpoint_dir} is a mountpoint':
        logger_runtime.error(f"the expected NAS mountpoint was not found at '{mountpoint_dir}'. "
                             f"Terminating..")
        return False
    logger_runtime.info(f"the expected NAS mountpoint was found at '{mountpoint_dir}'.")
    return True


def transfer_results_oncoservice(paths:dict,input_type:str,logger:Logger,testing:bool=True):
    run_name:str = paths['run_name']
    staging_temp_dir:Path = paths['staging_temp_dir']

    if input_type == 'run':
        onco_dir:Path = Path(str(paths['oncoservice_dir']))
        results_dir:Path = onco_dir / f'Analyseergebnisse{'_TEST' if testing else ''}' / run_name

    elif input_type == 'sample':
        onco_dir:Path = Path(str(paths['oncoservice_dir']) + '_TEST') if testing else Path(paths['oncoservice_dir'])
        results_dir:Path = onco_dir / 'Analyseergebnisse' / run_name

    rsync_path:str = paths['rsync_path']

    analysis_dir = staging_temp_dir / run_name

    rsync_call = f'{rsync_path} -r --checksum {str(f'{analysis_dir}/')} {str(results_dir)}'
    try:
        subp_run(rsync_call,check=True,shell=True)
    except CalledProcessError as e:
        message = f"Transferring results had failed: {e}"
        notify_bot(message)
        logger.error(message)
        raise RuntimeError(message)


def transfer_results_cbmed(paths:dict,logger:Logger,testing: bool=False):
    rsync_path:str = paths['rsync_path']
    run_name:str = paths['run_name']
    cbmed_results_dir:Path = paths['cbmed_results_dir']
    cbmed_seq_dir:Path = paths['cbmed_seq_dir']
    staging_temp_dir:Path = paths['staging_temp_dir']
    flowcell:str = paths['flowcell']
    run_seq_dir:Path = cbmed_seq_dir / paths['run_name']
    flowcell_cbmed_dir = cbmed_results_dir / 'flowcells' / flowcell
    data_cbmed_dir = flowcell_cbmed_dir / flowcell
    results_staging = staging_temp_dir / run_name
    dragen_cbmed_dir = cbmed_results_dir / 'dragen'
    results_cbmed_dir = dragen_cbmed_dir / flowcell / 'Results'
    samplesheet:Path = results_cbmed_dir / 'SampleSheet.csv'
    fastq_gen_seq_dir:Path = run_seq_dir / 'FastqGeneration'
    fastq_gen_results_dir:Path = results_cbmed_dir / 'FastqGeneration'
    data_cbmed_dir.mkdir(parents=True, exist_ok=True)
    results_cbmed_dir.mkdir(parents=True, exist_ok=True)

    if not run_seq_dir.exists or run_seq_dir.stat().st_size == 0:
        checksums_file_path = flowcell_cbmed_dir / f'{flowcell}.sha256'
        compute_checksums_call = (r'find '
                                  f'{str(run_seq_dir)} '
                                  r'-type f -exec sha256sum {} \; | tee  '
                                  f'{str(checksums_file_path)}')
        try:
            subp_run(compute_checksums_call, shell=True).check_returncode()
        except CalledProcessError as e:
            message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
            notify_bot(message)
            logger.error(message)
            raise RuntimeError(message)

    checksums_file_path = dragen_cbmed_dir / flowcell / f'{flowcell}_Results.sha256'
    compute_checksums_call = (r'find '
                              f'{str(results_staging)} '
                              r'-type f -exec sha256sum {} \; | tee  '
                              f'{str(checksums_file_path)}')
    try:
        subp_run(compute_checksums_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        notify_bot(message)
        logger.error(message)
        raise RuntimeError(message)

    if not run_seq_dir.exists or run_seq_dir.stat().st_size == 0:
        log_file_path = flowcell_cbmed_dir / 'CBmed_copylog.log'
        rsync_call = (f"{rsync_path} -r "
                      f"--out-format=\"%C %n\" "
                      f"--log-file {str(log_file_path)} "
                      f"--exclude='FastqGeneration' "
                      f"{str(run_seq_dir)}/ "
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

    if not samplesheet.exists() or samplesheet.stat().st_size == 0:
        rsync_call = (f"{rsync_path} "
                      f"{str(samplesheet)} "
                      f"{str(flowcell_cbmed_dir)}")
        try:
            subp_run(rsync_call,shell=True,check=True)
        except CalledProcessError as e:
            message = f"Transferring results had FAILED: {e}"
            notify_bot(message)
            logger.error(message)
            raise RuntimeError(message)

    return 0


def transfer_results_patho():
    pass


def get_server_ip() -> str:
    try:
        call = "ip route get 1.1.1.1 | awk '{print $7}'"
        result = subp_run(call, shell=True, check=True, text=True, capture_output=True)
        server_ip = result.stdout.split('\n', 1)[0].strip()

    except CalledProcessError as e:
        message = f"Failed to retrieve server's ID: {e.stderr}"
        raise RuntimeError(message)

    return server_ip


def load_config(configfile: str) -> dict:
    with open(configfile) as f:
        return yaml.safe_load(f)


def setup_paths(input_path:Path,input_type:str,tag:str,flowcell:str,config: dict) -> dict:
    paths: dict = dict()
    paths['ready_tags'] = config.get('ready_tags', [])
    paths['blocking_tags'] = config.get('blocking_tags', [])
    paths['rsync_path'] = sh_which('rsync')
    paths['testing_fast'] = config.get('testing_fast', False)
    paths['input_dir'] = input_path
    paths['flowcell'] = flowcell

    if paths['testing_fast']:
        paths['tso500_script_path'] = '/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/tso500_script_sub.sh'
    else:
        paths['tso500_script_path'] = '/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh'
        
    paths['staging_temp_dir'] = Path(config['staging_temp_dir'])
    paths['input_dir'] = input_path

    if input_type == 'run':
        paths['run_files_dir'] = input_path
        paths['run_dir'] = input_path.parent
        paths['run_name'] = paths['run_dir'].name
        paths['run_staging_temp_dir'] = paths['staging_temp_dir'] / paths['flowcell']
        paths['analysis_dir'] = paths['staging_temp_dir'] / paths['run_name']
        paths['oncoservice_dir'] = Path(config.get('oncoservice_novaseq6000_dir'))


    elif input_type == 'sample':
        paths['sample_dir'] = input_path
        paths['run_name'] = paths['sample_dir'].parent.parent.name
        paths['sample_id'] = paths['sample_dir'].name
        paths['sample_staging_temp_dir'] = paths['staging_temp_dir'] / paths['sample_id']
        paths['analysis_dir'] = paths['staging_temp_dir'] / paths['run_name']
        paths['oncoservice_dir'] = Path(config.get('oncoservice_novaseqx_dir'))

    else:
        RuntimeError(f'Unrecognised input type: {input_type}')

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    log_file = str(Path(config['logging_dir']) / f"TSO_{tag}_{timestamp}.log")

    paths['log_file'] = log_file
    paths['error_messages'] = config.get('error_messages', {})
    paths['tag'] = tag
    paths['testing'] = config.get('testing', False)
    paths['sx182_mountpoint'] = Path(config.get('sx182_mountpoint'))
    paths['sy176_mountpoint'] = Path(config.get('sy176_mountpoint'))
    paths['staging_temp_dir'] = Path(config.get('staging_temp_dir'))
    paths['cbmed_results_dir'] = Path(config.get('cbmed_results_dir'))
    paths['cbmed_seq_dir'] = Path(config.get('cbmed_seqencing_dir'))

    return paths


def check_mountpoint(paths: dict,
                     logger: Logger):
    sx182_mountpoint = Path(paths['sx182_mountpoint'])
    sy176_mountpoint = Path(paths['sy176_mountpoint'])

    if not sx182_mountpoint.is_dir():
        msg = f"Directory of a sx182 mountpoint '{sx182_mountpoint}' does not exist"
        notify_bot(msg)
        logger.error(msg)
        raise RuntimeError(msg)
    logger.info(f"Mountpoint found at '{sx182_mountpoint}'")

    if not sy176_mountpoint.is_dir():
        msg = f"Directory of a sx182 mountpoint '{sy176_mountpoint}' does not exist"
        notify_bot(msg)
        logger.error(msg)
        raise RuntimeError(msg)
    logger.info(f"Mountpoint found at '{sy176_mountpoint}'")

    if not is_nas_mounted(str(sx182_mountpoint), logger):
        msg = "Mountpoint check had failed"
        notify_bot(msg)
        logger.error(msg)
        raise RuntimeError(msg)
    logger.info("Mountpoint is mounted")


def check_structure(paths: dict,
                    logger: Logger):
    if not paths['input_dir'].is_dir():
        msg = f"Directory {paths['input_dir']} does not exist"
        notify_bot(msg)
        logger.error(msg)
        raise RuntimeError(msg)
    logger.info(f"Run directory found at {paths['input_dir']}")

    if not paths['staging_temp_dir'].is_dir():
        msg = f"Directory {paths['staging_temp_dir']} does not exist"
        notify_bot(msg)
        logger.error(msg)
        raise RuntimeError(msg)
    logger.info(f"Staging directory found at {paths['staging_temp_dir']}")


def check_docker_image(logger: Logger):

    try:
        result = subp_run(['docker', 'images'], stdout=subp_PIPE, stderr=subp_PIPE, text=True)
    except Exception as e:
        msg = f"Error checking docker image: {e}"
        notify_bot(msg)
        logger.error(msg)
        raise

    if 'dragen_tso500_ctdna' not in result.stdout:
        msg = "The dragen_tso500_ctdna Docker image wasn't found"
        notify_bot(msg)
        logger.error(msg)
        raise RuntimeError(msg)
    logger.info("The dragen_tso500_ctdna was found successfully")


def check_rsync(paths: dict, logger: Logger):

    if not paths['rsync_path']:
        msg = "Rsync not found on the system"
        notify_bot(msg)
        logger.error(msg)
        raise FileNotFoundError(msg)
    logger.info(f"Rsync found at: {paths['rsync_path']}")


def check_tso500_script(paths: dict, logger: Logger):

    script_path = Path(paths['tso500_script_path'])

    if not script_path.exists():
        msg = f"TSO500 script not found at {script_path}"
        notify_bot(msg)
        logger.error(msg)
        raise FileNotFoundError(msg)
    logger.info(f"TSO500 script found at {script_path}")


def stage_object(paths:dict,input_type:str,is_last_sample:bool,logger:Logger):
    notify_pipeline_status(step='staging',run_name=paths['run_name'],logger=logger,tag=paths['tag'],input_type=input_type,
                           is_last_sample=is_last_sample)

    rsync_call = f"{paths['rsync_path']} -rl {paths['input_dir']}/ {paths[f'{input_type}_staging_temp_dir']}"
    try:
        subp_run(rsync_call, check=True, shell=True)
    except CalledProcessError as e:
        err = e.stderr.decode() if e.stderr else str(e)
        msg = f"Staging failed (code {e.returncode}): {err}. Cleaning up..."
        notify_bot(msg)
        logger.error(msg)
        delete_directory(dead_dir_path=paths['run_staging_temp_dir'], logger_runtime=logger)
        raise RuntimeError(msg)


def process_object(input_type:str,paths:dict,is_last_sample:bool,logger:Logger):
    """
    Can be a run or a sample
    :param paths:
    :return:
    """
    notify_pipeline_status(step='running',run_name=paths['run_name'],logger=logger,tag=paths['tag'],input_type=input_type,
                           is_last_sample=is_last_sample)

    if input_type == 'run':
        tso_script_call = f"{paths['tso500_script_path']} --runFolder {paths['run_staging_temp_dir']} --analysisFolder {paths['analysis_dir']}"
        try:
            subp_run(tso_script_call,check=True,shell=True)
        except CalledProcessError as e:
            err_msg = paths['error_messages'].get(e.returncode, 'Unknown error')
            msg = f"TSO500 DRAGEN script had failed: {err_msg}. Cleaning up..."
            logger.error(msg)
            notify_bot(msg)
            delete_directory(dead_dir_path=paths['analysis_dir'], logger_runtime=logger)
            raise RuntimeError(msg)

    elif input_type == 'sample':
        tso_script_call = f"{paths['tso500_script_path']} --fastqFolder {paths['sample_staging_temp_dir']} --analysisFolder {paths['analysis_dir']}"
        try:
            subp_run(tso_script_call,check=True,shell=True)
        except CalledProcessError as e:
            err_msg = paths['error_messages'].get(e.returncode, 'Unknown error')
            msg = f"TSO500 DRAGEN script had failed: {err_msg}. Cleaning up..."
            logger.error(msg)
            notify_bot(msg)
            delete_directory(dead_dir_path=paths['analysis_dir'], logger_runtime=logger)
            raise RuntimeError(msg)


def transfer_results(paths: dict,input_type:str,is_last_sample:bool,testing:bool=True,logger:Logger=None):
    tag=paths['tag']

    notify_pipeline_status(step='transferring', run_name=paths['run_name'], logger=logger, tag=paths['tag'],
                           input_type=input_type,
                           is_last_sample=is_last_sample)

    try:
        if tag == 'ONC':
            transfer_results_oncoservice(paths=paths,input_type=input_type,logger=logger,testing=testing)
        elif tag == 'CBM':
            transfer_results_cbmed(paths=paths,logger=logger,testing=testing)
        else:
            raise ValueError(f"Unsupported run type: {input_type}")
    except Exception as e:
        logger.error(str(e))
        raise

    delete_directory(dead_dir_path=paths[f'{input_type}_staging_temp_dir'], logger_runtime=logger)
    delete_directory(dead_dir_path=paths['analysis_dir'], logger_runtime=logger)


def get_queue(pending_file:Path,queue_file:Path):
    assert pending_file.exists(), 'The pending file should exist'
    assert queue_file.exists(), 'The queue file should exist'

    pending_lock = FileLock(Path(str(pending_file) + '.lock'), timeout=10)

    if not pending_file.stat().st_size < 38:
        try:
            queue = pd.read_csv(pending_file, sep='\t')
            queue = queue.sort_values(by='Priority', ascending=True)
            queue_no_processing = queue.iloc[1:, ]
            queue_no_processing.to_csv(queue_file, sep='\t', index=False)

            pending_file.write_text('')
        finally:
            pending_lock.release()

    elif not queue_file.stat().st_size < 38:
        queue = pd.read_csv(queue_file, sep='\t')
        queue_no_processing = queue.iloc[1:, ]
        queue_no_processing.to_csv(queue_file, sep='\t', index=False)

    else:
        return

    return queue