from pathlib import Path
from subprocess import check_output, CalledProcessError


def get_repo_root() -> str:
    script_path = Path(__file__).parent
    try:
        root = check_output(
            f"cd {script_path} && git rev-parse --show-toplevel",
            text=True, shell=True
        ).strip()
        return root
    except CalledProcessError:
        raise RuntimeError("Not inside a git repository")