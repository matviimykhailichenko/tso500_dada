from subprocess import PIPE, Popen, STDOUT

# cmd = 'bcl-convert ' \
#       '--bcl-input-directory /mnt/CBmed_NAS3/Genomics/RNAseq_liquid/flowcells_TEST/test_big_run/250829_A01664_0550_AH3MYWDMX2 ' \
#       '--output-directory /staging/tmp/RNAseq_test'

cmd = 'python3 foo.py'

proc = Popen(
    cmd,
    stdout=PIPE,
    stderr=STDOUT,
    text=True,
    bufsize=1,
    shell=True
)

captured = []

for line in proc.stdout:
    print(line, end='')         # real-time output
    captured.append(line)       # storing for later check

proc.wait()

full_output = ''.join(captured)

if 'WARNING' in full_output:
    print('Oh shoot data is incomplete')
    raise RuntimeError("Bcl-convert reported incomplete data")