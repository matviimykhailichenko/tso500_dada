from pathlib import Path
from logging import Logger
from shutil import which as sh_which, rmtree as sh_rmtree, copy as sh_copy, move as sh_move, copytree as sh_copytree
from subprocess import run as subp_run, PIPE as subp_PIPE, CalledProcessError
from typing import Optional
import yaml
from logging_ops import notify_bot, notify_pipeline_status
from datetime import datetime
import pandas as pd
from filelock import FileLock
import numpy as np
from io import StringIO

def get_server_ip() -> str:
    try:
        call = "hostname -I"
        result = subp_run(call, shell=True, check=True, text=True, capture_output=True)
        server_ip = result.stdout.split()[-2]

    except CalledProcessError as e:
        message = f"Failed to retrieve server's ID: {e.stderr}"
        raise RuntimeError(message)

    return server_ip

with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    server = get_server_ip()
    server_availability_dir = Path(config['server_availability_dir'])
    server_idle_tag = server_availability_dir / server / config['server_idle_tag']
    server_busy_tag = server_availability_dir / server / config['server_busy_tag']

    import os

    print("os.path.exists (busy):", os.path.exists(server_busy_tag))
    try:
        os.stat(server_busy_tag)
        print("os.stat (busy): exists")
    except FileNotFoundError:
        print("os.stat (busy): does NOT exist")

    if server_idle_tag.exists() and not server_busy_tag.exists():
        print(True)
    elif server_busy_tag.exists() and not server_idle_tag.exists():
        print(False)
    else:
        message = f"There is a problem with busy/idle tags for the {server} server"
        notify_bot(message)
        raise RuntimeError(message)