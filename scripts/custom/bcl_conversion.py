from subprocess import run as subp_run, CalledProcessError

dragen_call = ("DRAGEN_TSO500.sh --resourcesFolder /staging/illumina/DRAGEN_TSO500/resources --hashtableFolder /staging/illumina/DRAGEN_TSO500/ref_hashtable --runFolder /mnt/Novaseq/07_Oncoservice/Runs/250314_TSO500_Onco/250314_A01664_0475_AHVF33DSXC"
               " --analysisFolder /mnt/Novaseq/07_Oncoservice/Runs/250314_TSO500_Onco/FastqGeneration"
               " --demultiplexOnly --sampleSheet /mnt/Novaseq/07_Oncoservice/Runs/250314_TSO500_Onco/250314_A01664_0475_AHVF33DSXC/SampleSheet.csv")

try:
    subp_run(dragen_call, check=True)
except CalledProcessError as e:
    print(e.stderr)