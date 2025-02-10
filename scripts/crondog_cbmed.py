from pathlib import Path
import yaml
from crondog_oncoservice import is_server_available, process_run, has_new_runs

# TODO add to other crontab scripts

def main():
    # Definitions
    with open('../config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        ready_tags = set(config['ready_tags'])
        blocking_tags = set(config['blocking_tags'])
        base_dir = config['base_dir']
        onco_dir = Path(base_dir) / config['oncoservice_dir']
        cbmed_dir = Path(base_dir) / config['cbmed_dir']
        results_dir = Path(base_dir) / config['results_dir']
        runs_dir = cbmed_dir / 'Runs'
        pending_onco_tag = Path(onco_dir / config['pending_run_tag'])
        pending_cbmed_tag = Path(cbmed_dir / config['pending_run_tag'])
        server_availability_dir = Path(base_dir) / config['server_availability_dir']
        server_idle_tag = server_availability_dir / config['server_idle_tag']
        server_busy_tag = server_availability_dir / config['server_busy_tag']

    if is_server_available(server_idle_tag, server_busy_tag):
        return

    if not has_new_runs(runs_dir,
                     blocking_tags,
                     ready_tags,
                     pending_cbmed_tag):
        return

    process_run(pending_cbmed_tag,
                server_busy_tag,
                results_dir)



if __name__ == "__main__":
    main()