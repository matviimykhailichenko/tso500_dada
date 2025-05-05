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
        onco_seq_dir:Path = Path(config['oncoservice_novaseq_dir'])
        test_pending_file = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/PENDING_oncoservice_runs.txt')
        test_onco_run_1:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_oncoservice_1')
        test_onco_run_2:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_oncoservice_2')

    server_ip = get_server_ip()
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    test_onco_run_seq_dir_1 = onco_seq_dir / 'test_run_1'
    test_onco_run_seq_dir_2 = onco_seq_dir / 'test_run_2'

    if not queue_file.exists():
        queue_file.touch()

    if not pending_file.exists():
        sh_copy(str(test_pending_file),str(pending_file))

    if not test_onco_run_seq_dir_1.exists():
        sh_copytree(str(test_onco_run_1),str(test_onco_run_seq_dir_1))

    if not test_onco_run_seq_dir_2.exists():
        sh_copytree(str(test_onco_run_2), str(test_onco_run_seq_dir_2))


def test_processing(setup_environment):
    processing_call = 'conda run -n tso500_dragen_pipeline python3 /mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/scripts/processing.py'
    for i in range(2):
        subp_run(processing_call,check=True,shell=True)
