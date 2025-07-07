from pathlib import Path
from logging import Logger
from shutil import which as sh_which, rmtree as sh_rmtree, copy as sh_copy, move as sh_move, copytree as sh_copytree
from subprocess import run as subp_run, PIPE as subp_PIPE, CalledProcessError
from typing import Optional
import yaml
from logging_ops import notify_bot, notify_pipeline_status
from datetime import datetime
import pandas as pd
from filelock import FileLock
import re
import numpy as np



def is_server_available() -> bool:
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        server = get_server_ip()
        server_availability_dir = Path(config['server_availability_dir'])
        server_idle_tag = server_availability_dir / server / config['server_idle_tag']
        server_busy_tag = server_availability_dir / server / config['server_busy_tag']

        if server_idle_tag.exists() and not server_busy_tag.exists():
            return True
        elif server_busy_tag.exists() and not server_idle_tag.exists():
            return False
        else:
            message = f"There is a problem with busy/idle tags for the {server} server"
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


def transfer_results_oncoservice(paths: dict, input_type: str, logger: Logger, testing: bool=True):
    run_name: str = paths['run_name']

    if input_type == 'run':
        results_dir:Path = Path(str(paths['onco_results_dir']) + '_TEST' if testing else '') / 'Runs'/ run_name
    elif input_type == 'sample':
        results_dir:Path = paths['onco_results_dir'] / run_name

    rsync_call = f'{paths['rsync_path']} -r --checksum --exclude="work" {str(f'{paths['analysis_dir']}/')} {str(results_dir)}'
    try:
        subp_run(rsync_call, check=True, shell=True)
    except CalledProcessError as e:
        message = f"Transferring results had failed: {e}"
        notify_bot(message)
        logger.error(message)
        raise RuntimeError(message)


def transfer_results_cbmed(paths: dict, input_type: str, logger: Logger, testing: bool = False):
    cbmed_results_dir: Path = paths['cbmed_results_dir']
    flowcell: str = paths['flowcell']
    flowcell_cbmed_dir: Path = cbmed_results_dir / 'flowcells' / flowcell
    data_cbmed_dir: Path = flowcell_cbmed_dir / flowcell
    dragen_cbmed_dir: Path = cbmed_results_dir / 'dragen'
    run_name: str = paths['run_name']
    cbmed_seq_dir: Path = paths['cbmed_seq_dir']
    run_seq_dir: Path = cbmed_seq_dir / flowcell
    rsync_path: str = paths['rsync_path']
    staging_temp_dir: Path = paths['staging_temp_dir']

    if input_type == 'sample':
        flowcell_run_dir: Path = cbmed_seq_dir / flowcell
        fastq_gen_seq_dir: Path = flowcell_run_dir / 'FastqGeneration'
    elif input_type == 'run':
        flowcell_run_dir: Path = cbmed_seq_dir / flowcell
        fastq_gen_seq_dir: Path = flowcell_run_dir / 'Logs_Intermediates' / 'FastqGeneration'

    results_staging: Path = staging_temp_dir / run_name
    results_cbmed_dir: Path = dragen_cbmed_dir / flowcell / 'Results'
    fastq_gen_results_dir: Path = flowcell_cbmed_dir / 'FastqGeneration'
    samplesheet_results_dir: Path = results_staging / paths['sample_sheet']
    samplesheet_cbmed_dir: Path = dragen_cbmed_dir/ flowcell / paths['sample_sheet']

    flowcell_cbmed_dir.mkdir(parents=True, exist_ok=True)
    results_cbmed_dir.mkdir(parents=True, exist_ok=True)
    fastq_gen_results_dir.mkdir(parents=True, exist_ok=True)

    # TODO Compute checksums for data and results on /staging/

    checksums_humgen = dragen_cbmed_dir / flowcell / f'{flowcell}_Results_HumGenNAS.sha256'
    checksums_call = (
        f'cd {str(results_staging)} && '
        "find . -type f -print0 | xargs -0 sha256sum | tee "
        f"{str(checksums_humgen)}"
    )
    try:
        subp_run(checksums_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        notify_bot(message)
        logger.error(message)
        # raise RuntimeError(message)

    if input_type == 'sample' and (not data_cbmed_dir.exists() or data_cbmed_dir.stat().st_size == 0):
        sh_copytree(flowcell_run_dir, flowcell_cbmed_dir / flowcell)

    if fastq_gen_results_dir.stat().st_size == 0:
        sh_copytree(fastq_gen_seq_dir, fastq_gen_results_dir)

    elif input_type == 'run':
        sh_copytree(paths['run_dir'], data_cbmed_dir)

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
        # raise RuntimeError(message)

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
            # raise RuntimeError(message)

    checksums_results_cbmed = dragen_cbmed_dir / flowcell / f'{flowcell}_Results.sha256'
    checksums_call = (
        f'cd {str(results_cbmed_dir)} && '
        "find . -type f -print0 | xargs -0 sha256sum | tee "
        f"{str(checksums_results_cbmed)}"
    )
    try:
        subp_run(checksums_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = f"Computing checksums for CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        notify_bot(message)
        logger.error(message)
        # raise RuntimeError(message)

    diff_call = (
        f'diff <(sort {str(checksums_humgen)}) <(sort {str(checksums_results_cbmed)})'
    )
    try:
        stdout = subp_run(diff_call, shell=True, capture_output=True,text=True, check=True, executable='/bin/bash').stdout.strip()
        if stdout is not None:
            message = f"Checksums in a CBmed run are different"
            # raise RuntimeError(message)
    except CalledProcessError as e:
        message = f"Computing diff for a CBmed run results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        notify_bot(message)
        logger.error(message)
        # raise RuntimeError(message)

    return 0


def transfer_results_patho(paths:dict, input_type:str, logger:Logger, testing:bool = True):
    run_name: str = paths['run_name']
    staging_temp_dir: Path = paths['staging_temp_dir']

    assert input_type == 'run', 'Patho only supposed to sequence runs from NSQ6000'
    # TODO Temporary until sx182 is fixed
    results_dir: Path = Path('/mnt/NovaseqXplus/08_Projekte/CBmed') / f'Analyseergebnisse' / run_name

    rsync_path: str = paths['rsync_path']

    analysis_dir = staging_temp_dir / run_name

    rsync_call = f'{rsync_path} -r --checksum {str(f'{analysis_dir}/')} {str(results_dir)}'
    try:
        subp_run(rsync_call, check=True, shell=True)
    except CalledProcessError as e:
        message = f"Transferring results had failed: {e}"
        notify_bot(message)
        logger.error(message)
        raise RuntimeError(message)


def transfer_results_research(paths:dict, input_type:str, logger:Logger, testing:bool = True):
    run_name: str = paths['run_name']
    staging_temp_dir: Path = paths['staging_temp_dir']

    results_dir: Path = paths['research_results_dir'] / paths['run_name']

    rsync_path: str = paths['rsync_path']

    analysis_dir = staging_temp_dir / run_name

    rsync_call = f'{rsync_path} -r --checksum {str(f'{analysis_dir}/')} {str(results_dir)}'
    try:
        subp_run(rsync_call, check=True, shell=True)
    except CalledProcessError as e:
        message = f"Transferring results had failed: {e}"
        notify_bot(message)
        logger.error(message)
        raise RuntimeError(message)


def get_server_ip() -> str:
    try:
        call = "hostname -I"
        result = subp_run(call, shell=True, check=True, text=True, capture_output=True)
        server_ip = result.stdout.split()[-2]

    except CalledProcessError as e:
        message = f"Failed to retrieve server's ID: {e.stderr}"
        raise RuntimeError(message)

    return server_ip


def load_config(configfile: str) -> dict:
    with open(configfile) as f:
        return yaml.safe_load(f)


def setup_paths(input_path: Path, input_type: str, tag: str, flowcell: str, config: dict,
                testing: bool = False, testing_fast: bool = False) -> dict:
    paths: dict = dict()
    paths['ready_tags'] = config.get('ready_tags', [])
    paths['blocking_tags'] = config.get('blocking_tags', [])
    paths['rsync_path'] = sh_which('rsync')
    paths['testing_fast'] = testing_fast
    paths['input_dir'] = input_path
    paths['flowcell'] = flowcell

    if paths['testing_fast']:
        paths[
            'tso500_script_path'] = '/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/tso500_script_sub.sh'
    elif tag == 'PAT':
        paths['tso500_script_path'] = '/usr/local/bin/DRAGEN_TSO500.sh'
    else:
        paths['tso500_script_path'] = '/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh'

    paths['staging_temp_dir'] = Path(config['staging_temp_dir'])
    paths['input_dir'] = input_path

    if input_type == 'run':
        paths['sample_sheet'] = 'SampleSheet.csv'
        paths['run_files_dir'] = input_path
        paths['run_dir'] = input_path.parent
        paths['run_name'] = paths['run_dir'].name
        paths['run_staging_temp_dir'] = paths['staging_temp_dir'] / paths['flowcell']
        paths['analysis_dir'] = paths['staging_temp_dir'] / paths['run_name']
        paths['oncoservice_dir'] = Path(config.get('oncoservice_novaseq6000_dir'))
        paths['onco_results_dir'] = paths['oncoservice_dir'] / 'Analyseergebnisse'

    elif input_type == 'sample':
        paths['sample_sheet'] = 'SampleSheet_Analysis.csv'
        paths['sample_dir'] = input_path
        paths['run_dir'] = input_path.parent.parent
        paths['run_name'] = f"{flowcell.split('_')[0][2:8]}_TSO500_Onco"
        paths['sample_id'] = paths['sample_dir'].name
        paths['sample_staging_temp_dir'] = paths['staging_temp_dir'] / paths['sample_id']
        paths['analysis_dir'] = paths['staging_temp_dir'] / paths['run_name']
        paths['oncoservice_dir'] = Path(config.get('oncoservice_novaseqx_dir') + '_TEST' if testing else '')
        paths['sample_sheet'] = paths['run_dir'] / 'SampleSheet_Analysis.csv'
        paths['onco_results_dir'] = paths['oncoservice_dir'] / 'Analyseergebnisse'

    paths['flowcell_dir'] = paths['run_dir'] / flowcell
    paths['analyzing_tag'] = paths['run_dir'] / config.get('analyzing_tag')
    paths['queued_tag'] = paths['run_dir'] / config.get('queued_tag')
    paths['analyzed_tag'] = paths['run_dir'] / config.get('analyzed_tag')

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    log_file = str(Path(config.get('pipeline_dir')) / 'logs' / f"TSO_{tag}_{timestamp}.log")

    paths['log_file'] = log_file
    paths['error_messages'] = config.get('error_messages', {})
    paths['tag'] = tag
    paths['testing'] = config.get('testing', False)
    paths['sx182_mountpoint'] = Path(config.get('sx182_mountpoint'))
    paths['sy176_mountpoint'] = Path(config.get('sy176_mountpoint'))
    paths['staging_temp_dir'] = Path(config.get('staging_temp_dir'))
    paths['cbmed_results_dir'] = Path(config.get('cbmed_sequencing_dir') + '_TEST' if testing else '')
    paths['cbmed_seq_dir'] = Path(config.get('cbmed_sequencing_dir') + '_TEST' if testing else '')
    paths['patho_seq_dir'] = Path(config.get('patho_seq_dir'))
    paths['research_results_dir'] = Path(config.get('research_dir')) / f'Analyseergebnisse{'_TEST' if testing else ''}'

    return paths

def check_mountpoint(paths: dict, logger: Logger):
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


def stage_object(paths:dict,input_type:str,last_sample_queue:bool,logger:Logger):
    notify_pipeline_status(step='staging',run_name=paths['run_name'],logger=logger,tag=paths['tag'],input_type=input_type,
                           last_sample_queue=last_sample_queue)

    rsync_call = f"{paths['rsync_path']} -rl {paths['input_dir']}/ {paths[f'{input_type}_staging_temp_dir']}"
    try:
        subp_run(rsync_call, check=True, shell=True)
    except CalledProcessError as e:
        err = e.stderr.decode() if e.stderr else str(e)
        msg = f"Staging failed (code {e.returncode}): {err}. Cleaning up..."
        notify_bot(msg)
        logger.error(msg)
        # delete_directory(dead_dir_path=paths['run_staging_temp_dir'], logger_runtime=logger)
        raise RuntimeError(msg)


def process_object(input_type:str,paths:dict,last_sample_queue:bool,logger:Logger):
    """
    Can be a run or a sample
    :param paths:
    :return:
    """
    notify_pipeline_status(step='running',run_name=paths['run_name'],logger=logger,tag=paths['tag'],input_type=input_type,
                           last_sample_queue=last_sample_queue)

    if input_type == 'run':
        tso_script_call = f"{paths['tso500_script_path']} --runFolder {paths['run_staging_temp_dir']} --analysisFolder {paths['analysis_dir']}"
        try:
            subp_run(tso_script_call,check=True,shell=True)
        except CalledProcessError as e:
            err_msg = paths['error_messages'].get(e.returncode, 'Unknown error')
            msg = f"TSO500 DRAGEN script had failed: {err_msg}. Cleaning up..."
            logger.error(msg)
            notify_bot(msg)
            # delete_directory(dead_dir_path=paths['analysis_dir'], logger_runtime=logger)
            raise RuntimeError(msg)

    elif input_type == 'sample':
        tso_script_call = (f"{paths['tso500_script_path']} --fastqFolder {paths['sample_staging_temp_dir']}  "
                           f"--sampleSheet {paths['sample_sheet']} --analysisFolder {paths['analysis_dir']} "
                           f"--sampleIDs {paths['sample_id']}")
        try:
            subp_run(tso_script_call,check=True,shell=True)
        except CalledProcessError as e:
            err_msg = paths['error_messages'].get(e.returncode, 'Unknown error')
            msg = f"TSO500 DRAGEN script had failed: {err_msg}. Cleaning up..."
            logger.error(msg)
            notify_bot(msg)
            # delete_directory(dead_dir_path=paths['analysis_dir'], logger_runtime=logger)
            raise RuntimeError(msg)


def transfer_results(paths: dict, input_type: str, last_sample_queue: bool, testing: bool = True, logger: Logger = None):
    tag = paths['tag']

    notify_pipeline_status(step='transferring', run_name=paths['run_name'], logger=logger, tag=paths['tag'],
                           input_type=input_type,
                           last_sample_queue=last_sample_queue)

    try:
        if tag == 'ONC':
            transfer_results_oncoservice(paths=paths, input_type=input_type,logger=logger,testing=testing)
        elif tag == 'CBM':
            transfer_results_cbmed(paths=paths, input_type=input_type, logger=logger, testing=testing)
        elif tag == 'PAT':
            transfer_results_patho(paths=paths, input_type=input_type, logger=logger, testing=testing)
        elif tag == 'TSO':
            transfer_results_research(paths=paths, input_type=input_type, logger=logger, testing=testing)
        else:
            raise ValueError(f"Unrecognised run type: {input_type}")
    except Exception as e:
        logger.error(str(e))
        raise

    delete_directory(dead_dir_path=paths[f'{input_type}_staging_temp_dir'], logger_runtime=logger)
    delete_directory(dead_dir_path=paths['analysis_dir'], logger_runtime=logger)

    notify_pipeline_status(step='finished', run_name=paths['run_name'], logger=logger, tag=paths['tag'],
                           input_type=input_type, last_sample_queue=last_sample_queue)


    # TODO add done tag
    # TODO delete QUEUED tag


def get_queue(pending_file:Path,queue_file:Path):
    assert pending_file.exists(), 'The pending file should exist'
    assert queue_file.exists(), 'The queue file should exist'

    pending_lock = FileLock(Path(str(pending_file) + '.lock'), timeout=10)

    if not pending_file.stat().st_size < 38:
        queue = pd.read_csv(pending_file, sep='\t')
        queue = queue.sort_values(by='Priority', ascending=True)
        queue_no_processing = queue.iloc[1:, ]
        queue_no_processing.to_csv(queue_file, sep='\t', index=False)

        pending_blank = '/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt'
        sh_copy(pending_blank, pending_file)
        pending_lock.release()

    elif not queue_file.stat().st_size < 38:
        queue = pd.read_csv(queue_file, sep='\t')
        queue_no_processing = queue.iloc[1:, ]
        queue_no_processing.to_csv(queue_file, sep='\t', index=False)

    else:
        return None

    return queue


def setup_paths_scheduler(testing: bool = True):
    paths = {}
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        paths['blocking_tags'] = config['blocking_tags']
        paths['ready_tags'] = config['ready_tags']
        paths['queued_tag'] = config['queued_tag']
        paths['sx182_mountpoint'] = config['sx182_mountpoint']
        paths['sy176_mountpoint'] = config['sy176_mountpoint']

        paths['patho_seq_dir'] = Path(config['patho_seq_dir'])
        paths['onco_seq_dir'] = Path(config['oncoservice_sequencing_dir'] + '_TEST') / 'Runs' if testing else Path(config['oncoservice_sequencing_dir']) / 'Runs'
        paths['cbmed_seq_dir'] = Path(config['cbmed_sequencing_dir'] + '_TEST') if testing else Path(config['cbmed_sequencing_dir'])
        paths['mixed_runs_dir'] = Path(config['mixed_runs_dir'] + '_TEST') if testing else Path(config['mixed_runs_dir'])
        paths['pipeline_dir'] = Path(config['pipeline_dir'])

        return paths


def scan_dir_nsq6000(flowcell_dir: Path):
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        blocking_tags = config['blocking_tags']
        ready_tags = config['ready_tags']

    txt_files = list(Path(flowcell_dir).glob('*.txt'))
    file_names = [path.name for path in txt_files]

    if any(f in blocking_tags for f in file_names):
        return None

    if all(tag in file_names for tag in ready_tags):
        notify_bot(str(flowcell_dir))
        return flowcell_dir


def scan_dir_nsqx(run_dir: Path, testing:bool = True):
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        blocking_tags = config['blocking_tags']
        ready_tags = config['ready_tags_nsqx']
    fastq_dir = None

    txt_files = list(Path(run_dir).glob('*.txt'))
    file_names = [path.name for path in txt_files]

    if any(f in blocking_tags for f in file_names):
        return None

    if not all(tag in file_names for tag in ready_tags):
        return None

    analyses_dir = run_dir / 'Analysis'

    if not analyses_dir.exists():
        return None

    for analysis_dir in analyses_dir.iterdir():
        analysis_complete_tag = analysis_dir / 'CopyComplete.txt'

        if not analysis_complete_tag.exists():
            continue

        fastq_dir = analysis_dir / 'Data' / 'BCLConvert' / 'fastq'

        if not fastq_dir.exists():
            return None
        else:
            break

    return fastq_dir

def append_pending_run(paths:dict, input_dir:Path, testing:bool = True):
    onco_seq_dir = paths['onco_seq_dir']
    cbmed_seq_dir = paths['cbmed_seq_dir']
    patho_seq_dir = paths['patho_seq_dir']
    pipeline_dir = paths['pipeline_dir']

    server = get_server_ip()
    pending_file = pipeline_dir.parent.parent / f'{server}_PENDING.txt'
    queued_tag = input_dir / paths['queued_tag']
    queued_tag.touch()

    priority_map = {onco_seq_dir: [1,'ONC'], cbmed_seq_dir: [2,'CMB'],patho_seq_dir: [3,'PAT']}
    priority = priority_map.get(input_dir.parent.parent)[0]
    tag = priority_map.get(input_dir.parent.parent)[1]

    entry = [str(input_dir), 'run', priority, tag, input_dir.name]
    new_run = pd.DataFrame([entry], columns=['Path','InputType','Priority','Tag','Flowcell'])
    if not pending_file.exists():
        pending_blank = '/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt'
        sh_copy(pending_blank, pending_file)

    if pending_file.stat().st_size < 38:
        with open(pending_file, 'a') as f:
            f.write('\n')
    new_run.to_csv(pending_file, sep='\t', mode='a', header=False, index=False)


def append_pending_samples(paths: dict, flowcell_name: str, input_dir: Path,  sample_ids:list, testing:bool = True):
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir = Path(config['pipeline_dir'])
        available_servers = config['available_servers']

    fastq_gen_dir = input_dir.parent.parent.parent.parent.parent / 'FastqGeneration'
    run_dir = fastq_gen_dir.parent
    queued_tag = run_dir / paths['queued_tag']

    paths = [fastq_gen_dir / id for id in sample_ids]
    priority_map = {'ONC': 1, 'CBM': 2, 'TSO': 3}
    tags = [s.split("-", 1)[1].split("_", 1)[0] for s in sample_ids]

    priorities = (int(priority_map.get(t)) for t in tags)

    entries = {'Path': paths, 'InputType': 'sample', 'Priority': priorities, 'Tag': tags, 'Flowcell': flowcell_name}
    new_samples = pd.DataFrame(entries)
    pedning_files = np.array_split(new_samples, len(available_servers))

    for server in available_servers:
        pending_file = pipeline_dir.parent.parent / f'{server}_PENDING.txt'
        if not pending_file.exists():
            pending_blank = '/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt'
            sh_copy(pending_blank, pending_file)
        if pending_file.stat().st_size < 37:
            with open(pending_file, 'a') as f:
                f.write('\n')

        pending = pd.DataFrame(pedning_files[available_servers.index(server)])
        pending.to_csv(pending_file, sep='\t', mode='a', header=False, index=False)

    queued_tag.touch()


def rearrange_fastqs(fastq_dir: Path) -> list:
    samples = []
    for fastq in fastq_dir.iterdir():
        if 'Undetermined' in str(fastq):
            continue
        sample_dir = fastq_dir.parents[4] / 'FastqGeneration' / f"{fastq.name.split('-',1)[0]}-{fastq.name.split('-',1)[1].split('_',1)[0]}"
        samples.append(str(sample_dir))
        if not sample_dir.exists():
            sample_dir.mkdir(parents=True)
        sh_move(str(fastq), str(sample_dir))
    samples = list(set(samples))

    return samples