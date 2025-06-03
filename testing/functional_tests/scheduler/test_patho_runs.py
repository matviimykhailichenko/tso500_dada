import pytest
from pathlib import Path
from shutil import copytree as sh_copytree, copy as sh_copy
from subprocess import run as subp_run
import yaml


@pytest.fixture()
def setup_environment():
    with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        patho_seq_dir:Path = Path(config['patho_seq_dir'] + '_TEST')
        pending_blank:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt')
        pending_pipeline_dir:Path = Path('/mnt/Novaseq/TSO_pipeline/10.200.215.35_PENDING.txt')
        test_patho_run_1:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_patho_1')
        test_patho_run_2:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_patho_2')

    test_patho_run_seq_dir_1 = patho_seq_dir / 'test_run_1'
    test_patho_run_seq_dir_2 = patho_seq_dir / 'test_run_2'

    sh_copy(pending_blank,pending_pipeline_dir)

    if not test_patho_run_seq_dir_1.exists():
        sh_copytree(str(test_patho_run_1),str(test_patho_run_seq_dir_1))

    if not test_patho_run_seq_dir_2.exists():
        sh_copytree(str(test_patho_run_2), str(test_patho_run_seq_dir_2))


def test_scheduler(setup_environment):
    scheduler_call = 'conda run -n tso500_dragen_pipeline python3 /mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/scripts/scheduler.py -t'
    for i in range(6):
        subp_run(scheduler_call,check=True,shell=True)
