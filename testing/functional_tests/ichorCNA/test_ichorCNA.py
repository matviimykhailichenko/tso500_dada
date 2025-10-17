import pytest
from pathlib import Path
from shutil import copytree as sh_copytree
from subprocess import CalledProcessError, check_output as subp_check_output
import sys
from datetime import datetime


def get_repo_root() -> str:
    script_path = Path(__file__).parent
    try:
        root = subp_check_output(
            f"cd {script_path} && git rev-parse --show-toplevel",
            text=True, shell=True
        ).strip()
        return root
    except CalledProcessError:
        raise RuntimeError("Not inside a git repository")

repo_root = get_repo_root()
sys.path.insert(0, str(repo_root))

from scripts.helpers import run_ichorCNA


@pytest.fixture()
def setup_environment(request):
    results_test_dir = Path('/mnt/Novaseq/TSO_pipeline/test_runs/test_samples_oncoservice_results')
    results_tmp_dir = Path(f'/staging/tmp/{datetime.today().strftime('%y%m%d')}_TSO500_Onco')

    if not results_tmp_dir.exists():
        sh_copytree(str(results_test_dir),str(results_tmp_dir))


def test_ichorCNA(setup_environment):
    paths = {}
    logger = None
    paths['run_name'] = f'{datetime.today().strftime('%y%m%d')}_TSO500_Onco'
    paths['sample_id'] = 'Sample_1-ONC'
    paths['ichorCNA_repo'] = '/mnt/NovaseqXplus/TSO_pipeline/resources/ichorCNA'
    paths['ichorCNA_wrapper'] = Path(repo_root) / 'scripts' / 'ichorCNA'
    input_type = 'sample'
    run_ichorCNA(paths=paths, input_type=input_type, logger=logger)

