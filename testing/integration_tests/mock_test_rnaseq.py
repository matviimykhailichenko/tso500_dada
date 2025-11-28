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
        rna_liquid_dir = Path(config['rnaseq_liquid_sequencing_dir'] + '_TEST')
        rna_solid_dir = Path(config['rnaseq_solid_sequencing_dir'] + '_TEST')
    test_ns6000_run = pipeline_dir / 'test_runs/mock/test_run_ns6000'
    server_ip = get_server_ip()
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    date = datetime.now().strftime("%Y%m%d")
    test_rna_liquid_run_seq_dir = rna_liquid_dir / f'{date}_RNAseq_b01_s01'
    test_rna_solid_run_seq_dir = rna_solid_dir / f'{date}_RNAseq_b01_s01'
    queued_tag_liquid = test_rna_liquid_run_seq_dir / '250123_A01664_0443_AH2J5YDMX2/QUEUED.txt'
    queued_tag_solid = test_rna_solid_run_seq_dir / '250123_A01664_0443_AH2J5YDMX2/QUEUED.txt'

    if queue_file.exists():
        queue_file.unlink()

    if pending_file.exists():
        pending_file.unlink()

    if not test_rna_liquid_run_seq_dir.exists():
        copytree(str(test_ns6000_run), str(test_rna_liquid_run_seq_dir))

    if not test_rna_solid_run_seq_dir.exists():
        copytree(str(test_ns6000_run), str(test_rna_solid_run_seq_dir))

    yield

    user_input = input("Test is finished. Proceed with teardown (delete directories)? (y/n): ")

    if user_input.lower() == 'y':
        print("Proceeding with teardown...")
        if queued_tag_liquid.exists():
            queued_tag_liquid.unlink()
        if queued_tag_solid.exists():
            queued_tag_solid.unlink()
        print(f"Removed the queued tag")

    else:
        print("Teardown skipped. Directories remain.")

    print("The test is finished.")



@pytest.mark.dependency(name='scheduler')
def test_scheduler(setup_environment):
    repo_root = get_repo_root()
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/scheduler.py -t'
    for i in range(2):
        run(cmd, check=True, shell=True)


@pytest.mark.dependency(depends=['scheduler'])
def test_processing():
    repo_root = get_repo_root()
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/processing.py -t -tf'
    for i in range(2):
        run(cmd,check=True,shell=True)
