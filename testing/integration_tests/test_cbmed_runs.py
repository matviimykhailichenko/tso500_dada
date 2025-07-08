import pytest
from pathlib import Path
from shutil import copy as sh_copy, copytree as sh_copytree
from subprocess import run as subp_run
import yaml


@pytest.fixture()
def setup_environment():
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        cbmed_seq_dir: Path = Path(config['cbmed_sequencing_dir'] + '_TEST')
        pending_blank: Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt')
        test_cbmed_run: Path = Path('/mnt/Novaseq/TSO_pipeline/test_runs/test_run_cbmed')
    server_ip = '10.200.215.35'
    queue_file = pipeline_dir.parent.parent / f'{server_ip}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server_ip}_PENDING.txt'
    test_cbmed_run_seq_dir = cbmed_seq_dir / '250620_BI_739_batch1'

    if queue_file.exists():
        sh_copy(str(pending_blank), str(pending_file))

    if pending_file.exists():
        sh_copy(str(pending_blank),str(pending_file))

    if not test_cbmed_run_seq_dir.exists():
        sh_copytree(str(test_cbmed_run),str(test_cbmed_run_seq_dir))


@pytest.mark.dependency(name="scheduling")
def test_scheduling(setup_environment):
    scheduling_call = 'python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/scheduler.py -t'
    subp_run(scheduling_call, check=True, shell=True)


@pytest.mark.dependency(depends=["scheduling"])
def test_processing():
    processing_call = 'python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/processing.py -t'
    subp_run(processing_call,check=True,shell=True)
