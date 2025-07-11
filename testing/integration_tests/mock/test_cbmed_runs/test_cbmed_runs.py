import pytest
from pathlib import Path
from shutil import copy as sh_copy, copytree as sh_copytree, rmtree as sh_rmtree
from subprocess import run as subp_run
import yaml


@pytest.fixture()
def setup_environment():
    with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        cbmed_seq_dir:Path = Path(config['cbmed_sequencing_dir'] + '_TEST')
    test_cbmed_run_1:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_cbmed_1')
    test_cbmed_run_2:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_cbmed_2')

    server_ip = '10.200.214.104'
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    test_cbmed_run_seq_dir_1 = cbmed_seq_dir / 'test_run_cbmed_1'
    test_cbmed_run_seq_dir_2 = cbmed_seq_dir / 'test_run_cbmed_2'

    if queue_file.exists():
        queue_file.unlink()

    if pending_file.exists():
        pending_file.unlink()

    if not test_cbmed_run_seq_dir_1.exists():
        sh_copytree(str(test_cbmed_run_1), str(test_cbmed_run_seq_dir_1))

    if not test_cbmed_run_seq_dir_2.exists():
        sh_copytree(str(test_cbmed_run_2), str(test_cbmed_run_seq_dir_2))

    yield

    queue_file.unlink()
    pending_file.unlink()


@pytest.mark.dependency(name='scheduler')
def test_scheduler(setup_environment):
    scheduler_call = 'python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/scheduler.py -t'
    subp_run(scheduler_call, check=True, shell=True)


@pytest.mark.dependency(depends=['scheduler'])
def test_processing():
    processing_call = 'python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/processing.py -t -tf'

    for i in range(2):
        subp_run(processing_call,check=True,shell=True)
