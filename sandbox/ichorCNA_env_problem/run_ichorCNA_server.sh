#!/bin/bash

# === Define file paths ===
R_SCRIPT="/mnt/NovaseqXplus/TSO_pipeline/resources/ichorCNA/scripts/runIchorCNA.R"
WIG="/staging/tmp/251017_TSO500_Onco/Results/ichorCNA/Sample_1-ONC_tumor.wig"
GC_WIG="/mnt/NovaseqXplus/TSO_pipeline/resources/ichorCNA/inst/extdata/gc_hg19_1000kb.wig"
MAP_WIG="/mnt/NovaseqXplus/TSO_pipeline/resources/ichorCNA/inst/extdata/map_hg19_1000kb.wig"
CENTROMERE="/mnt/NovaseqXplus/TSO_pipeline/resources/ichorCNA/inst/extdata/GRCh37.p13_centromere_UCSC-gapTable.txt"
PON="/media/matvii/30c92328-1f20-448d-a014-902558a05393/tso500_dragen_pipeline/scripts/ichorCNA/accessory_files/PoN_of_10controls_fromTSO_1000kb.txt_median.rds"
OUTDIR="/staging/tmp/251017_TSO500_Onco/Results/ichorCNA/Results_ichorCNA"

# === Run ichorCNA ===
Rscript "$R_SCRIPT" \
  --WIG "$WIG" \
  --gcWig "$GC_WIG" \
  --mapWig "$MAP_WIG" \
  --ploidy 'c(2,3,4)' \
  --normal 'c(0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95)' \
  --maxCN 7 \
  --id "Sample_1-ONC" \
  --estimateNormal TRUE \
  --estimatePloidy TRUE \
  --includeHOMD FALSE \
  --chrs 'c(1:22,"X")' \
  --chrTrain 'c(1:18)' \
  --centromere "$CENTROMERE" \
  --normalPanel "$PON" \
  --txnE 0.999 \
  --txnStrength 100000 \
  --scStates 'c(1,3)' \
  --estimateScPrevalence TRUE \
  --maxFracGenomeSubclone 0.5 \
  --maxFracCNASubclone 0.7 \
  --minSegmentBins 50 \
  --altFracThreshold 0.7 \
  --outDir "$OUTDIR"
