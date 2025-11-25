from subprocess import PIPE, Popen, STDOUT

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
for line in proc.stdout:
    print("RAW:", repr(line))     # <-- shows hidden chars
    print(line, end='')           # normal print
