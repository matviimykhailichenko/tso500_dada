import pytest
from pathlib import Path
from shutil import copytree as sh_copytree, move as sh_move
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
from scripts.logging_ops import setup_logger


@pytest.fixture()
def setup_environment(request):
    paths = {}
    paths['run_name'] = f'{datetime.today().strftime('%y%m%d')}_TSO500_Onco'
    paths['sample_id'] = 'Sample_1-ONC'
    paths['ichorCNA_repo'] = '/mnt/NovaseqXplus/TSO_pipeline/resources/ichorCNA'
    paths['ichorCNA_wrapper'] = Path(repo_root) / 'scripts' / 'ichorCNA'
    input_type = 'sample'
    results_test_dir = Path('/mnt/NovaseqXplus/TSO_pipeline/test_runs/test_samples_oncoservice_results')
    results_tmp_dir = Path(f'/staging/tmp/{datetime.today().strftime('%y%m%d')}_TSO500_Onco')
    sample_caller_dir = results_tmp_dir / f'Logs_Intermediates/DragenCaller/{paths['sample_id']}'
    sample_results_dir = results_tmp_dir / 'Results/ichorCNA'

    if not results_tmp_dir.exists():
        sh_copytree(str(results_test_dir),str(results_tmp_dir))

    bam_bai_files = list(sample_results_dir.glob('*.bam*'))

    yield paths, input_type, results_tmp_dir

    for file in bam_bai_files:
        sh_move(file, sample_caller_dir)


def test_ichorCNA(setup_environment):
    paths, input_type, results_tmp_dir = setup_environment
    logger = setup_logger(logger_name='test',log_file=f'{repo_root}/logs/test.log')
    run_ichorCNA(paths=paths, input_type=input_type, last_sample_queue=False, logger=logger)

