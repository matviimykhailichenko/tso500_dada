from subprocess import run as subp_run, PIPE as subp_PIPE, CalledProcessError



def get_server_ip() -> str:
    try:
        call = "hostname -I"
        result = subp_run(call, shell=True, check=True, text=True, capture_output=True)
        server_ip = result.stdout.split()[-2]

    except CalledProcessError as e:
        message = f"Failed to retrieve server's ID: {e.stderr}"
        raise RuntimeError(message)

    return server_ip



print(get_server_ip())