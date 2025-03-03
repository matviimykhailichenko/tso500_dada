import subprocess

process_call = ['process.sh']
try:
    subprocess.run(process_call).check_returncode()
except subprocess.CalledProcessError as e:
    message = f"Process failed with a return code: {e.returncode}."
    raise RuntimeError(message)
except FileNotFoundError:
    message = f"Process failed. Script not found"
    raise RuntimeError(message)

print('Ze process has run succesfulliah')