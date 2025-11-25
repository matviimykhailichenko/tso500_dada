from subprocess import Popen, PIPE, STDOUT

cmd = [
    'bcl-convert',
    '--bcl-input-directory', '/mnt/CBmed_NAS3/Genomics/RNAseq_liquid/flowcells_TEST/test_big_run/250829_A01664_0550_AH3MYWDMX2',
    '--output-directory', '/staging/tmp/RNAseq_test'
]

proc = Popen(
    cmd,
    stdout=PIPE,
    stderr=STDOUT,   # <-- merge stderr into stdout
    text=True,
    bufsize=1
)

captured = []

for line in proc.stdout:
    print("RAW:", repr(line))   # debug
    print(line, end='')
    captured.append(line)

proc.wait()

full_output = ''.join(captured)
print("RAW FULL:", repr(full_output))

if "WARNING" in full_output:
    print("Oh shoot data is incomplete")
else:
    print("NO WARNING FOUND")
