import pytest
from pathlib import Path
from shutil import copy as sh_copy, copytree as sh_copytree
from subprocess import run as subp_run
import yaml


@pytest.fixture()
def setup_environment():
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        cbmed_seq_dir:Path = Path(config['cbmed_sequencing_dir'])
        test_pending_file = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/PENDING_CBmed_samples.txt')
        test_cbmed_run:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_CBmed_nsqx')

    server_ip = '10.200.214.104'
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    test_cbmed_run_seq_dir = cbmed_seq_dir / '20250707_LH00803_0012_B232KMCLT3'

    if not queue_file.exists():
        queue_file.touch()

    if not pending_file.exists():
        sh_copy(str(test_pending_file),str(pending_file))

    if not test_cbmed_run_seq_dir.exists():
        sh_copytree(str(test_cbmed_run),str(test_cbmed_run_seq_dir))

    yield

    queue_file.unlink()
    pending_file.unlink()


def test_processing(setup_environment):
    processing_call = 'python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/processing.py'

    for i in range(8):
        subp_run(processing_call,check=True,shell=True)
