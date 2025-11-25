import pytest
from pathlib import Path
from shutil import copytree
from subprocess import run
from datetime import datetime
import yaml
from ..scripts.helpers import get_repo_root, get_server_ip



@pytest.fixture(scope="module")
def setup_environment():
    repo_root = get_repo_root()
    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir = Path(config['pipeline_dir'])
        rnaseq_dir = Path(config['rnaseq_sequencing_dir'] + '_TEST')
    test_ns6000_run = pipeline_dir / 'test_runs/test_run_ns6000'
    server_ip = get_server_ip()
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    date = datetime.now().strftime("%Y%m%d")
    test_rnaseq_run_seq_dir = rnaseq_dir / f'{date}_RNAseq_b01_s01'
    queued_tag = test_rnaseq_run_seq_dir / '250123_A01664_0443_AH2J5YDMX2/QUEUED.txt'
    failed_tag = test_rnaseq_run_seq_dir / '250123_A01664_0443_AH2J5YDMX2/FAILED.txt'

    if queue_file.exists():
        queue_file.unlink()

    if pending_file.exists():
        pending_file.unlink()

    if not test_rnaseq_run_seq_dir.exists():
        copytree(str(test_ns6000_run), str(test_rnaseq_run_seq_dir))

    yield

    user_input = input("Test is finished. Proceed with teardown (delete directories)? (y/n): ")

    if user_input.lower() == 'y':
        print("Proceeding with teardown...")
        if queued_tag.exists():
            queued_tag.unlink()
        if failed_tag.exists():
            failed_tag.unlink()
        print(f"Removed the queued tag")

    else:
        print("Teardown skipped. Directories remain.")

    print("The test is finished.")


@pytest.mark.dependency(name='scheduler')
def test_scheduler(setup_environment):
    repo_root = get_repo_root()
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/scheduler.py -t'
    run(cmd, check=True, shell=True)


@pytest.mark.dependency(depends=['scheduler'])
def test_processing():
    repo_root = get_repo_root()
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/processing.py -t'
    run(cmd,check=True,shell=True)
