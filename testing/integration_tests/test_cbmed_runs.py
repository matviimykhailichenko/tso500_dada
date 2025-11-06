import sys
import pytest
from pathlib import Path
from shutil import copy as sh_copy, copytree as sh_copytree
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
        cbmed_seq_dir: Path = Path(config['cbmed_sequencing_dir'] + '_TEST')
        pending_blank: Path = Path(f'{repo_root}/testing/files/PENDING_blank.txt')
        test_cbmed_run: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/test_runs/cbmed')
    server_ip = get_server_ip()
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    test_cbmed_run_seq_dir = cbmed_seq_dir / f'{datetime.now().strftime("%y%m%d")}_BI_735_batch1'

    if queue_file.exists():
        sh_copy(str(pending_blank), str(pending_file))

    if pending_file.exists():
        sh_copy(str(pending_blank),str(pending_file))

    if not test_cbmed_run_seq_dir.exists():
        sh_copytree(str(test_cbmed_run),str(test_cbmed_run_seq_dir))


@pytest.mark.dependency(name="scheduling")
def test_scheduling(setup_environment):
    cmd = '/staging/env/tso500_dragen_pipeline/bin/python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/scheduler.py -t'
    run(cmd, check=True, shell=True)


@pytest.mark.dependency(depends=["scheduling"])
def test_processing():
    cmd = '/staging/env/tso500_dragen_pipeline/bin/python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/processing.py -t'
    run(cmd,check=True,shell=True)
