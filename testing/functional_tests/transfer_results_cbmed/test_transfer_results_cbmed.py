import logging
from logging import Logger
import pytest
from pathlib import Path
from shutil import copytree as sh_copytree, copy as sh_copy, move as sh_move, which as sh_which
from subprocess import run as subp_run, CalledProcessError
import yaml
from datetime import datetime
from discord import SyncWebhook



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
    fastq_gen_results_dir: Path = results_cbmed_dir / 'FastqGeneration'
    if input_type == 'sample':
        fastq_gen_seq_dir: Path = run_seq_dir / 'FastqGeneration'
    elif input_type == 'run':
        fastq_gen_seq_dir: Path = results_staging / 'Logs_Intermediates' / 'FastqGeneration'

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

    if input_type == 'sample' and (not data_cbmed_dir.exists() or data_cbmed_dir.stat().st_size) == 0:
        sh_move(flowcell_run_dir, data_cbmed_dir)

    elif input_type == 'run':
        sh_move(paths['run_dir'], data_cbmed_dir)

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


def setup_paths(input_path: Path, input_type: str, tag: str, flowcell: str, config: dict,
                testing: bool = False) -> dict:
    paths: dict = dict()
    paths['ready_tags'] = config.get('ready_tags', [])
    paths['blocking_tags'] = config.get('blocking_tags', [])
    paths['rsync_path'] = sh_which('rsync')
    paths['testing_fast'] = config.get('testing_fast', False)
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
        paths['run_files_dir'] = input_path
        paths['run_dir'] = input_path.parent
        paths['run_name'] = paths['run_dir'].name
        paths['run_staging_temp_dir'] = paths['staging_temp_dir'] / paths['flowcell']
        paths['analysis_dir'] = paths['staging_temp_dir'] / paths['run_name']
        paths['oncoservice_dir'] = Path(config.get('oncoservice_novaseq6000_dir'))
        paths['onco_results_dir'] = paths['oncoservice_dir'] / 'Analyseergebnisse'

    elif input_type == 'sample':
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
    paths['cbmed_results_dir'] = Path(config.get('cbmed_sequencing_dir'))
    paths['cbmed_seq_dir'] = Path(config.get('cbmed_sequencing_dir') + '_TEST' if testing else '')
    paths['patho_seq_dir'] = Path(config.get('patho_seq_dir'))

    return paths


def setup_logger(logger_name: str,
                 log_file: str):
    logger = logging.getLogger(logger_name)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


def notify_bot(msg: str,
               url: str ='https://discord.com/api/webhooks/1334878015078793310/qENtDsst4aV31baSn9BJ8cf4mEhk75QTpC_rRF5HZ5V5Q_gKzHivFcs9IS5rTHNUVjLL'):
    if len(msg) > 2000:
        msg = f"{msg[:1993]} [...]"

    webhook = SyncWebhook.from_url(url)
    webhook.send(content=msg)


@pytest.fixture()
def setup_environment():
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        cbmed_seq_dir: Path = Path(config['cbmed_sequencing_dir'] + '_TEST')
        flowcell_name = '250123_A01664_0443_AH2J5YDMX2'
        test_cbmed_samples: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_onco_nsqx')
    test_cbmed_run_seq_dir = cbmed_seq_dir / flowcell_name
    test_results = Path('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_results')
    test_results_staging = Path('/staging/tmp/test_results')
    pending_blank: Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt')
    pending_file: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/10.200.215.35_PENDING.txt')
    test_sample = Path('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/transfer_results_cbmed/Sample_5-CBM')
    test_sample_staging = Path('/staging/tmp/Sample_5-CBM')

    if not test_cbmed_run_seq_dir.exists():
        sh_copytree(str(test_cbmed_samples),str(test_cbmed_run_seq_dir))
    if not test_results_staging.exists():
        sh_copytree(str(test_results), str(test_results_staging))
    if not test_sample_staging.exists():
        sh_copytree(str(test_sample), str(test_sample_staging))



def test_transfer_results_cbmed(setup_environment):
    flowcell_name = '250123_A01664_0443_AH2J5YDMX2'
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    paths = setup_paths(input_path=Path(f'/mnt/CBmed_NAS3/Genomics/TSO500_liquid_TEST/{flowcell_name}/FastqGeneration/Sample_5-CBM'),
                        input_type='sample',
                        tag='CBM',
                        flowcell=flowcell_name,
                        config=config)
    logger_runtime = setup_logger('transfer_results_cbmed',
                                  '/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/transfer_results_cbmed/last_execution.log')
    transfer_results_cbmed(paths=paths,
                           input_type='sample',
                           logger=logger_runtime,
                           testing=True)
