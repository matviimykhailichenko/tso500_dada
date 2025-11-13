from pathlib import Path
from subprocess import check_output, CalledProcessError, run
from crontab import CronTab



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


