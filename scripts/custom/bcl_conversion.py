from subprocess import run as subp_run, SubprocessError, CalledProcessError
from tabnanny import check

dragen_call = ("dragen --bcl-conversion-only true "
               "--bcl-input-directory /mnt/Novaseq/07_Oncoservice/Runs/250314_TSO500_Onco/250314_A01664_0475_AHVF33DSXC "
               "--output-directory /mnt/Novaseq/07_Oncoservice/Runs/250314_TSO500_Onco/250314_A01664_0475_AHVF33DSXC/FastqGeneration")

try:
    subp_run(dragen_call, check=True)
except CalledProcessError as e:
    print(e.stderr)