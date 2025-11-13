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

def enable_testing_mode(server_ip):
    last_part = server_ip.split('.')[-1]
    crontab_testing = f'/mnt/NovaseqXplus/TSO_pipeline/03_Production/tso500_dragen_pipeline/files/crontabs/crontab_{last_part}_testing'
    cron = CronTab(tabfile=crontab_testing)
    cron.write_to_user(user=True)

def disable_testing_mode(server_ip, repo_root):
    last_part = server_ip.split('.')[-1]
    crontab_production = f'{repo_root}/files/crontabs/crontab_{last_part}'
    cron = CronTab(tabfile=crontab_production)
    cron.write_to_user(user=True)
