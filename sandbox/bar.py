from subprocess import PIPE, Popen, STDOUT
from re import compile

cmd = 'bcl-convert ' \
      '--bcl-input-directory /mnt/CBmed_NAS3/Genomics/RNAseq_liquid/flowcells_TEST/test_big_run/250829_A01664_0550_AH3MYWDMX2 ' \
      '--output-directory /staging/tmp/RNAseq_test'

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

for line in proc.stderr:
    print(line, end='')
    captured.append(line)

proc.wait()

full_output = ''.join(captured)

ansi_escape = compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

clean_output = ansi_escape.sub('', full_output)

if 'WARNING:' in clean_output:
    print('Oh shoot data is incomplete')
    raise RuntimeError("Bcl-convert reported incomplete data")