import pytest
from pathlib import Path
from shutil import copytree, rmtree
from subprocess import run
import yaml
from ..scripts.helpers import get_repo_root, get_server_ip, generate_illumia_string



@pytest.fixture(scope="module")
def setup_environment():
    repo_root = get_repo_root()
    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir = Path(config['pipeline_dir'])
    test_research_nsx_run = pipeline_dir / 'test_runs/mock/run_nsx_tso'
    server_ip = get_server_ip()
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    test_run_research_dir = Path(config['research_dir'] + '_TEST') / 'Runs' / generate_illumia_string(instrument='nsx')

    if queue_file.exists():
        queue_file.unlink()

    if pending_file.exists():
        pending_file.unlink()

    if not test_run_research_dir.exists():
        copytree(str(test_research_nsx_run), str(test_run_research_dir))

    yield

    user_input = input("Test is finished. Proceed with teardown (delete directories)? (y/n): ")

    if user_input.lower() == 'y':
        print("Proceeding with teardown...")

        if test_research_nsx_run.exists():
            rmtree(test_research_nsx_run)
        print(f"Removed directory: {test_research_nsx_run}")

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
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/processing.py -t -tf'
    for i in range(2):
        run(cmd,check=True,shell=True)