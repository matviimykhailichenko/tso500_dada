from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from pathlib import Path
from shutil import rmtree

runs_file = 'runs'
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
testing_dir = Path('/media/matvii/30c92328-1f20-448d-a014-902558a05393/tso500_dragen_pipeline/watchdog')


# TODO Searches for tags directly in run directory, the assumption might be wrong!
class TagDog(FileSystemEventHandler):
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

        if (not any(f in blocking_tags for f in file_names) and
                (all(f in ready_tags for f in file_names))):
            # valid_runs.append(run_dir.name)
            with open(runs_file, 'a') as file:
                file.write(f'{run_dir}\n')

# TODO fix 3-time processing
def run_dog():
    if Path(runs_file).stat().st_size == 0:
        return

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
                    rmtree(run_to_process, ignore_errors=True)
                return  # Exit after processing one OC run

        # If no OC run found, process first regular run
        if runs_to_process:
            run_to_process = runs_to_process[0]
            print(f'Processing regular run {run_to_process}')
            runs_to_process.remove(run_to_process)
            with open(runs_file, 'w') as file:
                file.writelines(f'{line}\n' for line in runs_to_process)
            rmtree(run_to_process, ignore_errors=True)


def watch_directory(path):
    if not Path(path).exists():
        raise FileNotFoundError(f"Directory does not exist: {path}")
    event_handler = TagDog()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            run_dog()
            time.sleep(3)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    watch_directory(testing_dir)