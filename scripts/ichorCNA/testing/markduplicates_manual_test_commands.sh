# WARNING - these tests were carries out using the picard tools version 3.4.0 from Bnejamin's TSO500ichorCNA conda environment o nthe MedBioNode cluster!
#           Expect version issues if you have a version mismatch!
[[ "$($(which picard) MarkDuplicatesWithMateCigar --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')" != "3.4.0" ]] && echo "⚠️  WARNING: MarkDuplicatesWithMateCigar version is not 3.4.0"

# I had to find out where the job was run from the following lines (get slurm job ID from executed command):
# (TSO500ichorCNA) -bash-5.2$ srun --ntasks=1 --cpus-per-task=24 --nice bash -c 'eval "$(conda shell.bash hook)" && conda activate TSO500ichorCNA && mkdir -p /media/temp/2062/L186_1-ONC_tumor/ && samtools sort --threads 12 -n "/home/isilon/HumGenTempData/for_Raul_TSO500/Data_fo
#r_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/L186_1-ONC_tumor.bam" | samtools fixmate -m - - | samtools sort --threads 6 -o /media/temp/2062/L186_1-ONC_tumor/L186_1-ONC_tumor.mateFixed.sorted.bam -'
#srun: job 1763101 queued and waiting for resources
#srun: job 1763101 has been allocated resources


#(TSO500ichorCNA) -bash-5.2$ sacct -j 1763101 --format=JobID,JobName,NodeList
#JobID           JobName        NodeList
#------------ ---------- ---------------
#1763101            bash           sy094
#1763101.ext+     extern           sy094
#1763101.0          bash           sy094


# how londg did it take?
#(TSO500ichorCNA) -bash-5.2$ sacct -j 1763101 --format=JobID,JobName,State,Start,End,Elapsed
#JobID           JobName      State               Start                 End    Elapsed
#------------ ---------- ---------- ------------------- ------------------- ----------
#1763101            bash  COMPLETED 2025-07-07T18:16:13 2025-07-07T18:39:58   00:23:45
#1763101.ext+     extern  COMPLETED 2025-07-07T18:16:13 2025-07-07T18:39:58   00:23:45
#1763101.0          bash  COMPLETED 2025-07-07T18:16:13 2025-07-07T18:39:58   00:23:45


# srun command to test piped name-sorting ->into-> samtools fixmate ->into-> coordinate-sorting again
srun --ntasks=1 --cpus-per-task=24 --nice bash -c 'eval "$(conda shell.bash hook)" && conda activate TSO500ichorCNA && mkdir -p /media/temp/2062/L186_1-ONC_tumor/ && samtools sort --threads 12 -n "/home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/L186_1-ONC_tumor.bam" | samtools fixmate -m - - | samtools sort --threads 6 -o /media/temp/2062/L186_1-ONC_tumor/L186_1-ONC_tumor.mateFixed.sorted.bam -'
# (above command was executed on sy095 -> temp dir is node-local)
# I rsynced the BAM file back to the ISILON NAS from the sy094 node and indexed it
# rsync (from on sy095):
rsync --checksum $TMP/L186_1-ONC_tumor/L186_1-ONC_tumor.mateFixed.sorted.bam /home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/  # on sy095
# index (on the sy096 node again with TSO500ichorCNA conda env active):
samtools index /home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/L186_1-ONC_tumor.mateFixed.sorted.bam  # on the sy096 node again with TSO500ichorCNA conda env active

# test MarkDuplicatesWithMateCigar and MArkDuplicates commands on supposedly "mate fixed" file (on the sy096 node again with TSO500ichorCNA conda env active):
#ANALYZE_SCAFFOLD='chr1'
#INPUT_BAM=/home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/L186_1-ONC_tumor.mateFixed.sorted.bam
#SAMPLE_NAME='L186_1-ONC_tumor.mateFixed.sorted'
#TMP_OUT=/media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed
# mkdir -p "${TMP_OUT}/tmp"
srun --ntasks=1 --cpus-per-task=24 --nice bash -c 'eval "$(conda shell.bash hook)" && conda activate TSO500ichorCNA && rm -rf /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed/ && mkdir -p /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed/tmp/ && samtools view -h -F 12 --uncompressed /home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/L186_1-ONC_tumor.mateFixed.sorted.bam chr1 | picard -Xmx2g MarkDuplicatesWithMateCigar --INPUT /dev/stdin --CREATE_INDEX true --TMP_DIR /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed/tmp/ --OUTPUT /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed/L186_1-ONC_tumor.mateFixed.sorted-chr1.bam --METRICS_FILE /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed/L186_1-ONC_tumor.mateFixed.sorted-chr1_scaffold_metrics --ASSUME_SORTED true --MINIMUM_DISTANCE 750 --COMPRESSION_LEVEL 2 --MAX_RECORDS_IN_RAM 1000000 --OPTICAL_DUPLICATE_PIXEL_DISTANCE 2500 --REMOVE_DUPLICATES false && rsync -rl --checksum /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed/ /home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/ && mv /home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/L186_1-ONC_tumor.mateFixed.sorted-chr1.bai /home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/L186_1-ONC_tumor.mateFixed.sorted-chr1.bam.bai && rm -rf /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed/'
# worked (first without parameters in brackets):
# (--MINIMUM_DISTANCE 750 --COMPRESSION_LEVEL 2 --MAX_RECORDS_IN_RAM 1000000 --OPTICAL_DUPLICATE_PIXEL_DISTANCE 2500 --REMOVE_DUPLICATES false)
# LIBRARY UNPAIRED_READS_EXAMINED READ_PAIRS_EXAMINED     SECONDARY_OR_SUPPLEMENTARY_RDS  UNMAPPED_READS  UNPAIRED_READ_DUPLICATES        READ_PAIR_DUPLICATES    READ_PAIR_OPTICAL_DUPLICATES    PERCENT_DUPLICATION     ESTIMATED_LIBRARY_SIZE
# L186_1-ONC      0       7720744 66129   0       0       1141648 0       0.147868        23464385
#
# the histogram output indicates that these are all non-optical duplicates which might not be true
# (in case there actually would be optical duplicates)
# since these are collapsed consensus reads and not originally sequenced reads
# (i.e., reads from multiple sequencing clusters got collapsed into a single consensus read)

# worked also with full parameters (Elapsed time: 2.16 minutes. for chr1)
# LIBRARY UNPAIRED_READS_EXAMINED READ_PAIRS_EXAMINED     SECONDARY_OR_SUPPLEMENTARY_RDS  UNMAPPED_READS  UNPAIRED_READ_DUPLICATES        READ_PAIR_DUPLICATES    READ_PAIR_OPTICAL_DUPLICATES    PERCENT_DUPLICATION     ESTIMATED_LIBRARY_SIZE
# L186_1-ONC      0       7720744 66129   0       0       1141648 0       0.147868        23464385
# -> this result suggests that the parameters might not be necessary in the TSO500 liquid collapsed UMI groups setup
#    (tagged records checked wit hsamtools view -f 0x400: 2,283,297 = READ_PAIR_DUPLICATES x 2 +1)


# show duplicates-flag-marked alignments: samtools view -f 0x400 <IN.BAM> | less
# (you can also just count the lines)

# original mark duplicates command with minimal adaptation to make it run:
srun --ntasks=1 --cpus-per-task=24 --nice bash -c 'eval "$(conda shell.bash hook)" && conda activate TSO500ichorCNA && rm -rf /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed-RaulsMD/tmp/; mkdir -p /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed-RaulsMD/tmp/ && samtools view -h -F 12 --uncompressed /home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/L186_1-ONC_tumor.mateFixed.sorted.bam chr1 | picard -Xmx2g MarkDuplicates -I /dev/stdin -O /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed-RaulsMD/L186_1-ONC_tumor-RaulsMD.mateFixed.sorted-chr1.bam -M /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed-RaulsMD/L186_1-ONC_tumor-RaulsMD.mateFixed.sorted-chr1.markdup.metrics --CREATE_INDEX true --VALIDATION_STRINGENCY LENIENT --TMP_DIR /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed-RaulsMD/tmp/ --ASSUME_SORTED true --OPTICAL_DUPLICATE_PIXEL_DISTANCE 2500 && mv /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed-RaulsMD/L186_1-ONC_tumor-RaulsMD.mateFixed.sorted-chr1.bai /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed-RaulsMD/L186_1-ONC_tumor-RaulsMD.mateFixed.sorted-chr1.bam.bai && rsync -rl --checksum /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed-RaulsMD/ /home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/ && rm -rf /media/temp/2062/L186_1-ONC_tumor-chr1_MateFixed-RaulsMD/'
# Elapsed time: 1.18 minutes for chr1
# DID NOT WORK: creates empty BAM file!
# -rwxrwxr-- 1 o_spiegl humangenetik  830 Jul  8 13:43 /home/isilon/HumGenTempData/for_Raul_TSO500/Data_for_ichor/250611_TSO500_Onco-RECREATIONNEWSCRIPT/L186_1-ONC_tumor-RaulsMD.mateFixed.sorted-chr1.bam
