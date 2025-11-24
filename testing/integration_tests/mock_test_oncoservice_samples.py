import pytest
from pathlib import Path
from shutil import copy, copytree, rmtree
from subprocess import run
import yaml
from ..scripts.helpers import get_repo_root, get_server_ip, generate_illumia_string


@pytest.fixture()
def setup_environment():
    repo_root = get_repo_root()
    server_ip = get_server_ip()
    illumina_string = generate_illumia_string()
    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir = Path(config['pipeline_dir'])
        onco_seq_dir = Path(config['oncoservice_sequencing_dir'] + '_TEST') / 'Runs'
        pending_blank = Path(f'{repo_root}/files/PENDING_blank.txt')
        test_onco_run = Path('/mnt/NovaseqXplus/TSO_pipeline/test_runs/mock/test_run_nsx_onc')
    pending_file = pipeline_dir / f'{server_ip}_PENDING.txt'
    test_onco_run_seq_dir = onco_seq_dir / illumina_string

    if test_onco_run_seq_dir.exists():
        rmtree(test_onco_run_seq_dir)
    if pending_file.exists():
        pending_file.unlink()

    copytree(str(test_onco_run), str(test_onco_run_seq_dir))
    copy(str(pending_blank),str(pending_file))

    yield


def test_scheduler(setup_environment):
    repo_root = get_repo_root()
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/scheduler.py -t'

    run(cmd,check=True,shell=True)
