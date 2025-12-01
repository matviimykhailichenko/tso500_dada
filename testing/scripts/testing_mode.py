import argparse
from crontab import CronTab
import sys
from pathlib import Path
from helpers import get_server_ip, get_repo_root


def enable_testing_mode():
    server_ip = get_server_ip()
    last_part = server_ip.split('.')[-1]
    crontab_testing = Path(f'/mnt/NovaseqXplus/TSO_pipeline/03_Production/tso500_dragen_pipeline/files/crontabs/crontab_{last_part}_testing')
    if not crontab_testing.exists():
        print(f"Crontab file not found at: {crontab_testing}")
        sys.exit(1)
    cron = CronTab(tabfile=str(crontab_testing))
    cron.write_to_user(user=True)
    print(f"Enabled testing mode for server {server_ip}")

def disable_testing_mode():
    server_ip = get_server_ip()
    repo_root = get_repo_root()
    last_part = server_ip.split('.')[-1]
    crontab_production = Path(f'{repo_root}/files/crontabs/crontab_{last_part}')
    if not crontab_production.exists():
        print(f"Crontab file not found: {crontab_production}")
        sys.exit(1)
    cron = CronTab(tabfile=str(crontab_production))
    cron.write_to_user(user=True)
    print(f"Disabled testing mode for server {server_ip}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enable or disable testing mode for a given server.")
    parser.add_argument("-e", "--enable", help="Enable testing mode for the specified server IP")
    parser.add_argument("-d", "--disable", help="Disable testing mode for the specified server IP and repo root")

    args = parser.parse_args()

    if args.enable:
        enable_testing_mode(args.enable)
    elif args.disable:
        disable_testing_mode(args.disable)
    else:
        parser.print_help()
