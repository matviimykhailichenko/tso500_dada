from pathlib import Path
from subprocess import check_output, CalledProcessError, run
from re import fullmatch
from datetime import datetime



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


def get_server_ip() -> str:
    try:
        call = "hostname -I"
        result = run(call, shell=True, check=True, text=True, capture_output=True)
        server_ip = result.stdout.split()[-2]

    except CalledProcessError as e:
        message = f"Failed to retrieve server's ID: {e.stderr}"
        raise RuntimeError(message)

    return server_ip


def generate_illumia_string(instrument: str) -> str:
    today = datetime.now().strftime("%Y%m%d")
    if instrument == 'nsx':
        illumina_sting = f"{today}_LH00803_2749_CICEAJ7JXH"
    elif instrument == 'ns6000':
        illumina_sting = f"{today}_A01664_2749_CICEAJ7JXH"

    return illumina_sting


def find_illumina_string(dir: Path) -> str | None:
    for subdir in dir.iterdir():
        m = fullmatch(r'^\d{6}_A01664_\d{4}_[A-Z0-9]{10}$', subdir.name)
        if m:
            return m.group()
    return None
