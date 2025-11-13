import sys
import pytest
from pathlib import Path
from shutil import copy as sh_copy, copytree as sh_copytree
from subprocess import run
from datetime import datetime
import yaml
from ..scripts.helpers import get_repo_root, get_server_ip, enable_testing_mode, disable_testing_mode


@pytest.fixture()
def setup_environment():
    server_ip = get_server_ip()
    enable_testing_mode(server_ip=server_ip)
    repo_root = get_repo_root()
    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        cbmed_seq_dir: Path = Path(config['cbmed_sequencing_dir'] + '_TEST')
        pending_blank: Path = Path(f'{repo_root}/files/PENDING_blank.txt')
        test_cbmed_run: Path = Path(f'{pipeline_dir}/test_runs/cbmed')
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    test_cbmed_run_seq_dir = cbmed_seq_dir / f'{datetime.now().strftime("%y%m%d")}_BI_735_batch1'

    if queue_file.exists():
        sh_copy(str(pending_blank), str(pending_file))

    if pending_file.exists():
        sh_copy(str(pending_blank),str(pending_file))

    if not test_cbmed_run_seq_dir.exists():
        sh_copytree(str(test_cbmed_run),str(test_cbmed_run_seq_dir))

    yield

    disable_testing_mode(server_ip=server_ip, repo_root=repo_root)


@pytest.mark.dependency(name="scheduling")
def test_scheduling(setup_environment):
    repo_root = get_repo_root()
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/scheduler.py -t'
    run(cmd, check=True, shell=True)


@pytest.mark.dependency(depends=["scheduling"])
def test_processing():
    repo_root = get_repo_root()
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/processing.py -t'
    run(cmd,check=True,shell=True)
