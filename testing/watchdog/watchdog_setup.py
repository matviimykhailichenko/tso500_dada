from pathlib import Path

testing_dir = Path('/media/matvii/30c92328-1f20-448d-a014-902558a05393/tso500_dragen_pipeline/watchdog')
run_dir = testing_dir / 'run'
run_dir.mkdir(exist_ok=True)
ready_tags = [
    'SequenceComplete.txt',
    'CopyComplete.txt',
    'RTAComplete.txt'
]


for tag in ready_tags:
    Path(run_dir).joinpath(tag).touch()