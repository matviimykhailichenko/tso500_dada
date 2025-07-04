import pytest
from pathlib import Path
from shutil import copytree as sh_copytree, copy as sh_copy, move as sh_move
from subprocess import run as subp_run
import yaml



@pytest.fixture()
def setup_environment(request):
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        cbmed_seq_dir: Path = Path(config['cbmed_sequencing_dir'] + '_TEST')
        test_cbmed_samples: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/test_runs/test_samples_cbmed')
    test_cbmed_run_seq_dir = cbmed_seq_dir / '240830_A01664_0367_AHL3VCDSXC'
    pending_blank: Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt')
    pending_file: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/10.200.215.35_PENDING.txt')

    sh_copy(str(pending_blank), str(pending_file))
    if not test_cbmed_run_seq_dir.exists():
        sh_copytree(str(test_cbmed_samples),str(test_cbmed_run_seq_dir))


@pytest.mark.dependency(name="scheduling")
def test_scheduling(setup_environment):
    scheduling_call = 'python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/scheduler.py -t'
    subp_run(scheduling_call, check=True, shell=True)


@pytest.mark.dependency(depends=["scheduling"])
def test_processing():
    processing_call = 'python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/processing.py -t'
    for i in range(2):
        subp_run(processing_call,check=True,shell=True)
