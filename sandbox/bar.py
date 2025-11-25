from subprocess import Popen, PIPE, STDOUT

cmd = 'bcl-convert --bcl-input-directory /mnt/CBmed_NAS3/Genomics/RNAseq_liquid/flowcells_TEST/test_big_run/250829_A01664_0550_AH3MYWDMX2 --output-directory /staging/tmp/RNAseq_test'

proc = Popen(
    cmd,
    stdout=PIPE,
    stderr=STDOUT,
    text=True,
    bufsize=1,
    shell=True
)

warning_found = False

while True:
    line = proc.stdout.readline()

    if not line:
        if proc.poll() is not None:  # process has ended
            break
        continue  # no line yet, keep looping

    print(line, end="")

    if "WARNING" in line:
        warning_found = True
        print("=== WARNING DETECTED — stopping run ===")
        proc.terminate()
        break

# only call wait AFTER termination or loop exit
proc.wait()

if warning_found:
    raise RuntimeError("Bcl-convert reported incomplete data")
