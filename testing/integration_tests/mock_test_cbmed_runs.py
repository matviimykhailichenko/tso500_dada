import pytest
from pathlib import Path
from shutil import copytree
from subprocess import run
from datetime import datetime
import yaml
from ..scripts.helpers import get_repo_root, get_server_ip



@pytest.fixture()
def setup_environment():
    repo_root = get_repo_root()
    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        cbmed_seq_dir:Path = Path(config['cbmed_sequencing_dir'] + '_TEST')
    test_cbmed_run_1:Path = Path(f'{repo_root}/testing/integration_tests/mock/test_run_cbmed_1')
    test_cbmed_run_2:Path = Path(f'{repo_root}/testing/integration_tests/mock/test_run_cbmed_2')

    server_ip = get_server_ip
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    test_cbmed_run_seq_dir_1 = cbmed_seq_dir / f'{datetime.now().strftime("%y%m%d")}_BI_735_batch1'
    test_cbmed_run_seq_dir_2 = cbmed_seq_dir / f'{datetime.now().strftime("%y%m%d")}_BI_735_batch2'

    if queue_file.exists():
        queue_file.unlink()

    if pending_file.exists():
        pending_file.unlink()

    if not test_cbmed_run_seq_dir_1.exists():
        copytree(str(test_cbmed_run_1), str(test_cbmed_run_seq_dir_1))

    if not test_cbmed_run_seq_dir_2.exists():
        copytree(str(test_cbmed_run_2), str(test_cbmed_run_seq_dir_2))


@pytest.mark.dependency(name='scheduler')
def test_scheduler(setup_environment):
    repo_root = get_repo_root()
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/scheduler.py -t'
    run(cmd, check=True, shell=True)


@pytest.mark.dependency(depends=['scheduler'])
def test_processing():
    repo_root = get_repo_root()
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/processing.py -t -tf'
    for i in range(2):
        run(cmd,check=True,shell=True)
