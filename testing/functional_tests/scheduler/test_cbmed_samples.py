import pytest
from pathlib import Path
from shutil import copy as sh_copy, copytree as sh_copytree, rmtree as sh_rmtree
from subprocess import run as subp_run
import yaml



@pytest.fixture()
def setup_environment():
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        cbmed_seq_dir: Path = Path(config['cbmed_sequencing_dir'] + '_TEST')
        pending_blank: Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt')
        test_cbmed_run: Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_onco_nsqx')
    server_ip = '10.200.214.104'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    test_cbmed_run_seq_dir = cbmed_seq_dir / 'test_run_cbmed_nsqx'

    if test_cbmed_run_seq_dir.exists():
        sh_rmtree(test_cbmed_run_seq_dir)
    if pending_file.exists():
        pending_file.unlink()

    sh_copytree(str(test_cbmed_run), str(test_cbmed_run_seq_dir))
    sh_copy(str(pending_blank),str(pending_file))

    yield


def test_scheduler(setup_environment):
    scheduler_call = 'python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/scheduler.py -t'
    for i in range(1):
        subp_run(scheduler_call,check=True,shell=True)
