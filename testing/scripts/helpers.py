from pathlib import Path
from subprocess import check_output, CalledProcessError, run
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

def generate_illumia_string:
    today = datetime.now().strftime("%Y%m%d")
    illumina_sting = f"{today}_A01664_2749_CICEAJ7JXH"

    return illumina_sting