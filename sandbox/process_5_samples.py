from subprocess import run
import pytest
from pathlib import Path
from subprocess import CalledProcessError, check_output as subp_check_output
import yaml



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
cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/processing.py'

for i in range(5):
    run(cmd, check=True, shell=True)
