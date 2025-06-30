import pytest
from pathlib import Path
from shutil import copytree as sh_copytree, copy as sh_copy, move as sh_move
from subprocess import run as subp_run
import yaml



with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    pipeline_dir: Path = Path(config['pipeline_dir'])
    onco_seq_dir: Path = Path(config['oncoservice_novaseqx_dir'] + '_TEST') / 'Runs'
    test_onco_samples: Path = Path('/mnt/Novaseq/TSO_pipeline/test_runs/test_samples_oncoservice')
pending_file_samples = '/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/test_oncoservice_samples/PENDING_oncoservice_samples.txt'
pending_file_35 = pipeline_dir.parent.parent / f'10.200.215.35_PENDING.txt'
pending_file_104 = pipeline_dir.parent.parent / f'10.200.214.104_PENDING.txt'
queue_file_104 = pipeline_dir.parent.parent / f'10.200.214.104_QUEUE.txt'
pending_blank = '/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt'
test_onco_run_seq_dir = onco_seq_dir / 'test_run_onco_nsqx'
fastq_analysis_dir = test_onco_run_seq_dir / 'Analysis/1/Data/BCLConvert/fastq'
fastq_gen_dir = test_onco_run_seq_dir / 'FastqGeneration'
queued_tag = test_onco_run_seq_dir / config['queued_tag']
analyzed_tag = test_onco_run_seq_dir / config['analyzed_tag']



for sample_dir in fastq_gen_dir.iterdir():
    for fastq in sample_dir.iterdir():
        if not fastq_analysis_dir.exists():
            fastq_analysis_dir.mkdir()
        sh_move(str(fastq), fastq_analysis_dir)

if queued_tag.exists():
        queued_tag.unlink()
if analyzed_tag.exists():
    analyzed_tag.unlink()
if queue_file_104.exists():
    queue_file_104.unlink()
if pending_file_104.exists():
    pending_file_104.unlink()