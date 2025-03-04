from pathlib import Path
from scripts.helpers import delete_directory

dead_dir = Path('/home/matvii/PycharmProjects/TSO_500_DRAGEN_pipeline/sandbox/delete_directory/dead_dir')
delete_directory(dead_dir)