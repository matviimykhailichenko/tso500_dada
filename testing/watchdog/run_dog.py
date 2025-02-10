from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from filelock import Timeout, FileLock
import time
from pathlib import Path
from shutil import rmtree
import sys
import os


# TODO Should be in config

onco_tag = 'OC'
ready_tags = [
   "SequenceComplete.txt",
   "CopyComplete.txt",
   "RTAComplete.txt"
]
blocking_tags = [
   "ANALYZED.txt",
   "ANALYSIS_FAILED.txt",
   "FAILED.txt",
   "IGNORED.txt"
]

# used by TagDog:
testing_dir = Path('/media/matvii/30c92328-1f20-448d-a014-902558a05393/tso500_dragen_pipeline/scripts')
runs_file = Path(testing_dir /'runs')
is_processing = False

# TODO Searches for tags directly in run directory, the assumption might be wrong!
class TagDog(FileSystemEventHandler):
    runs_file_lock = FileLock(str(runs_file) + '.loc', timeout=10)
    def on_created(self, event):

        if event.is_directory:
            return

        filename = Path(event.src_path).name

        if not filename in ready_tags:
            return

        Path(event.src_path)
        run_dir = Path(event.src_path).parent
        txt_files = list(Path(run_dir).glob('*.txt'))
        file_names = [path.name for path in txt_files]

        if any(f in blocking_tags for f in file_names):
            return

        if all(tag in file_names for tag in ready_tags):
            with self.runs_file_lock.acquire(timeout=10):
                # valid_runs.append(run_dir.name)
                with open(runs_file, 'a') as file:
                    file.write(f'{run_dir}\n')

# TODO fix
def daemonize():
    # First fork (detaches from parent)
    try:
        pid = os.fork()
        if pid > 0:
            # Parent process exits
            sys.exit(0)
    except OSError as err:
        sys.exit(f'fork #1 failed: {err}')

    # Decouple from parent environment
    os.chdir('/')  # Change working directory
    os.setsid()  # Create new session
    os.umask(0)  # Reset file mode creation mask

    # Second fork (relinquish session leadership)
    try:
        pid = os.fork()
        if pid > 0:
            # Parent process exits
            sys.exit(0)
    except OSError as err:
        sys.exit(f'fork #2 failed: {err}')


def process_runs():
    # TODO check if needed
    global is_processing

    if (is_processing or
            not Path(runs_file).exists() or
            Path(runs_file).stat().st_size == 0):
        return

    try:
        is_processing = True
        # Read first line and rest of file
        with open(runs_file, 'r') as f:
            runs_to_process = [line.strip() for line in f.readlines()]
            # First check for OC run
            for run_to_process in runs_to_process:
                if onco_tag in run_to_process:
                    print(f'Processing onco run {run_to_process}')
                    runs_to_process.remove(run_to_process)
                    # Write back remaining runs
                    with open(runs_file, 'w') as file:
                        file.writelines(f'{line}\n' for line in runs_to_process)
                        # rmtree(run_to_process, ignore_errors=True)
                    return  # Exit after processing one OC run

            # If no OC run found, process first regular run
            if runs_to_process:
                run_to_process = runs_to_process[0]
                print(f'Processing regular run {run_to_process}')
                runs_to_process.remove(run_to_process)
                with open(runs_file, 'w') as file:
                    file.writelines(f'{line}\n' for line in runs_to_process)
                # rmtree(run_to_process, ignore_errors=True)
    finally:
        is_processing = False


def watch_directory(path):
    if not Path(path).exists():
        raise FileNotFoundError(f"Directory does not exist: {path}")
    event_handler = TagDog()
    # TODO> use list of directories that are to be watched in hte same way
    observer = Observer(timeout=10.)
    # TODO recurcive not good
    observer.schedule(event_handler, path)
    observer.start()

    try:
        while True:
            if (Path(path) / 'kill_dog').exists():
                observer.stop()
                observer.join()
                (Path(path) / 'kill_dog').unlink()
                break
            process_runs()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# TODO Add messaging to capture exceptions
def main():
    try:
        if not testing_dir.exists():
            sys.exit(f"Error: Directory {testing_dir} does not exist")

        # Start the daemon
        daemonize()
        watch_directory(testing_dir)

    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()