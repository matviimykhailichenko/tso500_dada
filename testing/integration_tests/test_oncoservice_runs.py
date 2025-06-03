import pytest
from pathlib import Path
from scripts.helpers import get_server_ip
from shutil import copy as sh_copy, copytree as sh_copytree
from subprocess import run as subp_run
import yaml


@pytest.fixture()
def setup_environment():
    with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        onco_seq_dir:Path = Path(config['oncoservice_novaseq6000_dir']) / 'Runs_TEST'
        test_pending_file = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/PENDING_oncoservice_runs.txt')
        test_onco_run:Path = Path('/mnt/Novaseq/TSO_pipeline/test_runs/test_run_oncoservice')

    server_ip = get_server_ip()
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    test_onco_run_seq_dir = onco_seq_dir / 'test_run_oncoservice'

    if not queue_file.exists():
        queue_file.touch()

    if not pending_file.exists():
        sh_copy(str(test_pending_file),str(pending_file))

    if not test_onco_run_seq_dir.exists():
        sh_copytree(str(test_onco_run),str(test_onco_run_seq_dir))

    yield

    queue_file.unlink()
    pending_file.unlink()


def test_processing(setup_environment):
    processing_call = 'conda run -n tso500_dragen_pipeline python3 /mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/scripts/processing.py'
    subp_run(processing_call, check=True, shell=True)
