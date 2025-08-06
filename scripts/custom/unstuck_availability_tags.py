from shutil import rmtree as sh_rmtree
from pathlib import Path


sh_rmtree(Path('/mnt/NovaseqXplus/TSO_pipeline/server_availability'))

Path('/mnt/NovaseqXplus/TSO_pipeline/server_availability/10.200.215.35/IDLE.txt').parent.mkdir(parents=True, exist_ok=True)
Path('/mnt/NovaseqXplus/TSO_pipeline/server_availability/10.200.215.35/IDLE.txt').touch()
Path('/mnt/NovaseqXplus/TSO_pipeline/server_availability/10.200.214.104/IDLE.txt').parent.mkdir(parents=True, exist_ok=True)
Path('/mnt/NovaseqXplus/TSO_pipeline/server_availability/10.200.214.104/IDLE.txt').touch()
