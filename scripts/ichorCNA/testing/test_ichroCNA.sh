#!/usr/bin/env bash
set -euo pipefail
# Execute from /testing dir

# Check argument
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <ichorCNA_installation_dir>"
    exit 1
fi

ICHOR_DIR="$1"

# Validate directory
if [[ ! -d "$ICHOR_DIR" ]]; then
    echo "ERROR: Directory not found: $ICHOR_DIR"
    exit 1
fi

OUTDIR="./Results_ichorCNA"

mkdir -p "${OUTDIR}"

Rscript "${ICHOR_DIR}/scripts/runIchorCNA.R" \
    --WIG "test.wig" \
    --gcWig "${ICHOR_DIR}/inst/extdata/gc_hg19_1000kb.wig" \
    --mapWig "${ICHOR_DIR}/inst/extdata/map_hg19_1000kb.wig" \
    --ploidy "c(2,3,4)" \
    --normal "c(0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95)" \
    --maxCN 7 \
    --id "P732_2-ONC" \
    --estimateNormal TRUE \
    --estimatePloidy TRUE \
    --includeHOMD FALSE \
    --chrs "c(1:22,\"X\")" \
    --chrTrain "c(1:18)" \
    --centromere "${ICHOR_DIR}/inst/extdata/GRCh37.p13_centromere_UCSC-gapTable.txt" \
    --normalPanel "../accessory_files/PoN_of_10controls_fromTSO_1000kb.txt_median.rds" \
    --txnE 0.999 \
    --txnStrength 100000 \
    --scStates "c(1,3)" \
    --estimateScPrevalence TRUE \
    --maxFracGenomeSubclone 0.5 \
    --maxFracCNASubclone 0.7 \
    --minSegmentBins 50 \
    --altFracThreshold 0.7 \
    --libdir "${ICHOR_DIR}" \
    --outDir "${OUTDIR}"
