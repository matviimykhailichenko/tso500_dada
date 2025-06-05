import pytest
from pathlib import Path
from shutil import copytree as sh_copytree
from subprocess import run as subp_run
import yaml


@pytest.fixture()
def setup_environment():
    with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        cbmed_seq_dir:Path = Path(config['cbmed_nsq6000_dir'] + '_TEST')
        test_cbmed_run_1:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_cbmed_1')
        test_cbmed_run_2:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_cbmed_2')

    test_cbmed_run_seq_dir_1 = cbmed_seq_dir / 'test_run_1'
    test_cbmed_run_seq_dir_2 = cbmed_seq_dir / 'test_run_2'


    if not test_cbmed_run_seq_dir_1.exists():
        sh_copytree(str(test_cbmed_run_1),str(test_cbmed_run_seq_dir_1))

    if not test_cbmed_run_seq_dir_2.exists():
        sh_copytree(str(test_cbmed_run_2), str(test_cbmed_run_seq_dir_2))


def test_scheduler(setup_environment):
    scheduler_call = 'conda run -n tso500_dragen_pipeline python3 /mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/scripts/scheduler.py -t'
    for i in range(1):
        subp_run(scheduler_call,check=True,shell=True)
