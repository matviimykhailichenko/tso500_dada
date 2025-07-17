from pathlib import Path
from shutil import copytree as sh_copytree, rmtree as sh_rmtree



base_dir = Path('/mnt/NovaseqXplus/07_Oncoservice_TEST/Analyseergebnisse/250710_TSO500_Onco')
test_run = Path('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_nsqx_processed')
run_seq_dir = Path('/mnt/NovaseqXplus/07_Oncoservice_TEST/Runs/20250710_LH00803_0014_A232WCWLT3')
archived_dir = Path('/mnt/NovaseqXplus/HuGe_Diagnostik-ARCHIV_TEST/2025/TSO500/250710_TSO500_Onco')
test_results = Path('/mnt/NovaseqXplus/07_Oncoservice/Analyseergebnisse/250710_TSO500_Onco')
results_dir = Path('/mnt/NovaseqXplus/07_Oncoservice_TEST/Analyseergebnisse/250710_TSO500_Onco')

if (base_dir / 'ARCHIVED.txt').exists():
    (base_dir / 'ARCHIVED.txt').unlink()

if not (base_dir / 'ANALYZED.txt').exists():
    (base_dir / 'ANALYZED.txt').touch()

if (base_dir / 'ARCHIVING_FAILED.txt').exists():
    (base_dir / 'ARCHIVING_FAILED.txt').unlink()

if not run_seq_dir.exists():
    sh_copytree(test_run, run_seq_dir)

if not results_dir.exists():
    sh_copytree(test_results, results_dir)

if archived_dir.exists():
    sh_rmtree(archived_dir)