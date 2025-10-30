#!/usr/bin/env bash
#set -e
#: Title       : From BAM to wig (requires sorted BAMs with .bai files)
#: Date        : 01-07-2024
#: Author      : Raúl Mejía based on Isaac Lazzeri's script
#: Version     : 1.0
#: Description : 
#: Arguments   : $1 path to reference genome (It has to be already indexed. In PATH/TO/REFGENOME/ there should also be the index file fai or bai extensions) (PATH/TO/REFGENOME/ucsc.hg19.fasta)
#:             : $2 
#: Notes       : PICARD variable need to be set to /PATH/TO/PICARD/picard.jar
#: Notes       : require hmmcopy, ichorcna, picard -> change the following paths to yours
#: Notes       : make sure you can run picard just writing "/PATH/TO/PICARD/picard" in the terminal
#: Example Usag:  
#Path_2_IchorScript=/home/isilon/users/o_mejiaped/Code_bk/ichorCNA_Installation_Repo_Running/Usable_Script/Panel_of_Normals
#my_BAMs_dir=/home/isilon/users/o_mejiaped/Project_wise/Avenio_vs_sWGS_tumor_fraction/Data/1_Picked_PseudoControls/2_BAMs
#path_hmm=/usr/bin # doesn't matter
#reference_genome=/home/isilon/users/o_mejiaped/Common_Data_4_Projects/Reference_Genome/UCSC/hg38/hg38.fa 
#path_to_ichor=/home/isilon/users/o_mejiaped/Code_bk/ichorCNA_Installation_Repo_Running/ichorCNA 
# bash $Path_2_IchorScript/From_SortedBam_2_WIG_files.sh -idir $my_BAMs_dir -phmm $path_hmm -gref $reference_genome -pichor $path_to_ichor  &> $my_BAMs_dir/Logfile.log #


#--------------------------------------------------------------------------------------------------
#************************************FUNCTION****************************************************
#--------------------------------------------------------------------------------------------------

function apply_to_each_fastq(){
#arg1 = function
#arg2 = NAMES
#arg3 = ref_genome
#arg4 = ref_fasta ${HG_FASTA}
#arg5 = /PATH/TO/ichorCNAdir 
#echo "Printing apply_to_each_fastq function arguments"
#echo $1 
#echo ${2}
#echo $3 
#echo $4 
#echo $5   
    for i in ${2}; do 
        #echo $1 $i $3 $4 $5
        $1 $i $3 $4 $5
    done
}

function pipeline(){
#arg1 = base_unique_sample_name
#arg2 = ref_genome
#arg3 = ref_fasta ${HG_FASTA}
#arg4 = /PATH/TO/ichorCNAdir
#echo "Printing pipline function arguments"
#echo $1 
#echo ${2}
#echo $3 
#echo $4
        #merging_lanes ${1}
        #allign ${2} ${1}_R1_merged.fastq ${1}_R2_merged.fastq ${1}
        #echo allign ${2} ${1}_R1_merged.fastq ${1}_R2_merged.fastq ${1}
        #sort_sam ${1}
        mark_duplicates ${1}
        ichor ${1} ${2} ${3} ${4}
}

function merging_lanes(){
# arg1 = base_unique_sample_name
# merge the lanes of the fastq files for
# forward and revers R1 and R2
if ! ls | grep ${1}_R1_merged.fastq; then
    cat ${1}*_R1* > ${1}_R1_merged.fastq
fi
if ! ls | grep ${i}_R2_merged.fastq; then
    cat ${1}*_R2* > ${1}_R2_merged.fastq
fi
}

function allign(){
# arg1 = ref_genome
# arg2 = R1_merged.fastq
# arg3 = R2_merged.fastq
# arg4 = base_unique_sample_name
#echo "Printing allign function arguments"
#echo $1 
#echo ${2}
#echo $3 
#echo $4

if ! ls | grep ${4}.sam; then
    echo "STEP1: Alligning with bwa mem -t 12 ${1} ${2} ${3} TO ${4}."
    #bwa mem -t 25 ${1} ${2} ${3} > ${4}.sam # RAMP Changed the number of threads # anyway it is commented lines above
else
    echo "STEP1: Alligning with bwa mem ${1} ${2} ${3} TO ${4} already carried out."
fi
}

function sort_sam(){
#arg1 = base_unique_sample_nam

echo "STEP2: Sorting sam"
if ! ls | grep "^${1}.bam$"; then
    picard SortSam I=${1}.sam \
    O="${1}.bam" SO=coordinate CREATE_INDEX=true
else
    echo "STEP2: Already done"
fi
}

function mark_duplicates(){
#arg1 = base_unique_sample_nam

echo "STEP3: Marking duplicate"
if ! ls | grep "^${1}.markdup.bam$"; then
    picard MarkDuplicates \
    I="${1}.bam" \
    O=${1}.markdup.bam \
    M=${1}.markdup.metrics \
    CREATE_INDEX=TRUE \
    VALIDATION_STRINGENCY=LENIENT
    mv ${1}.markdup.bai ${1}.markdup.bam.bai
else
    echo "STEP3: Already done"
fi
}


function ichor(){

#arg1 = base_unique_sample_nam
#arg2 = ref_genome
#arg3 = ref_fasta ${HG_FASTA}
#arg4 = /PATH/TO/ichorCNAdir
#mv ${1}.markdup.bai ${1}.markdup.bam.bai

echo "STEP4: running readcounter"
if ! ls | grep "^${1}.wig$"; then
echo "***************************************************************"
echo ${1}
echo "***************************************************************"
readCounter --window 1000000 --quality 20 \
--chromosome "chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY" \
${1}.markdup.bam > ${1}.wig
else
    echo "STEP4: Already done"
fi

#gcCounter -w 1000000 \
#--chromosome "chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY" \
#${2} > ${3}

echo "STEP5: running ichorCNA"
if ! ls | grep "Results_ichorCNA_${1}"; then

mkdir ./Results_ichorCNA_${1} # Raúl added create the directory to save results
Rscript $4/scripts/runIchorCNA.R \
--WIG ${1}.wig \
--gcWig $4/inst/extdata/gc_hg19_1000kb.wig \
--mapWig $4/inst/extdata/map_hg19_1000kb.wig \
--ploidy "c(2,3,4)" \
--normal "c(0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95)" \
--maxCN 7 \
--id ${1} \
--estimateNormal TRUE \
--estimatePloidy TRUE \
--includeHOMD FALSE \
--chrs "c(1:22,\"X\")" \
--chrTrain "c(1:18)" \
--centromere $4/inst/extdata/GRCh37.p13_centromere_UCSC-gapTable.txt \
--normalPanel /home/isilon/users/o_mejiaped/Project_wise/Avenio_vs_sWGS_tumor_fraction/Data/TSO500/CustomPoN_backup/CustomPoN_TS500_1MB_Hg19/PoN_of_10controls_fromTSO_1000kb.txt_median.rds \
--chrTrain "c(1:18)" \
--txnE 0.999 \
--txnStrength 100000 \
--scStates "c(1,3)" \
--estimateScPrevalence TRUE \
--maxFracGenomeSubclone 0.5 \
--maxFracCNASubclone 0.7 \
--minSegmentBins 50 \
--altFracThreshold 0.7 \
--lambdaScaleHyperParam 3 \
--outDir ./Results_ichorCNA_${1}

else
    echo "STEP5: Already done"
fi

}

#--------------------------------------------------------------------------------------------------
#***************************************MAIN*******************************************************
#--------------------------------------------------------------------------------------------------
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -idir|--input_dir)
    INPUT_DIR="$2"
    shift # past argument
    shift # past value
    ;;
    -phmm|--path_to_hmm)
    PATH_TO_HMM="$2"
    shift # past argument
    shift # past value
    ;;
    -gref|--reference_genome)
    REF_GENOME="$2"
    shift # past argument
    shift # past value
    ;;
    -pichor|--path_to_ichorCNA)
    PATH_TO_ICHOR="$2"
    shift # past argument
    shift # past value
    ;;
    -ppicard|--path_to_picard)
    PATH_TO_PICARD="$2"
    shift # past argument
    shift # past value
    ;;
    -h|--help)
    echo ""
    echo "------------"
    echo "Description:"
    echo "------------"
    echo "	This pipline run the pipline for all samples in a directory. File need to be gzipped. They will be unzipped at the beginning of the pipeline."
    echo "	Different lanes are merged together for forward and reversed reads (R1 and R2). File are alligned with bwa mem, sorted and duplicates marked"
    echo "	with picard. Finally ichorCNA pipline is called and run"
    echo ""
    echo "------"
    echo "Usage:"
    echo "------"
    echo "	bash pip_ichor_path_independent.sh -idir path_to_input_dir -phmm path_to_hmm -panaconda path_to_anaconda"
    echo "	-gref path_to_ref_genome -pichor path_to_ichorcna -ppicard path_to_picard"
    echo ""  
    echo "--------"
    echo "Example:"
    echo "--------" 
    echo "	bash pip_ichor_path_independent.sh -idir PATH/TO/FASTQs -phmm /usr/local/bin/hmmcopy_utils/bin -panaconda /home/user/bcbio/anaconda/bin/"
    echo "	-gref /home/user/Documents/reference_genomes/HG19/hg19.fa -pichor ~/ichorCNA-master -ppicard /PATH/TO/picard"
    echo ""
    echo "----------"
    echo "Arguments:"
    echo "----------"
    echo "	-idir or --input_dir: path to the directory containing pairended fastq files to be analyzed"
    echo "	-phmm or --path_to_hmm: path to the hmm"
    echo "	-gref or --reference_genome: path to the genome. Need to be indexed"
    echo "	-pichor or --path_to_ichorCNA: path to the ichorCNA directory cloned by the ichorCNA repo"
    echo "	-ppicard or --path_to_picard: path to picard"
    exit 1
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done

#adding HMM and anaconda to the path (if anaconda is not needed just uncomment it)
export PATH=$PATH:$PATH_TO_HMM #/usr/local/bin/hmmcopy_utils/bin  #"/PATH/TO/HMMCOPY"

#setting variables 
REF_GENOME=$REF_GENOME #"/home/isy/Documents/PhD/Bioinformatics/reference_genomes/HG19/hg19.fa"
ICHOR=$PATH_TO_ICHOR #"~/Downloads/ichorCNA-master"
HG_FASTA=hg19.gc.wig
 
echo $INPUT_DIR
echo $PATH_TO_HMM
echo $REF_GENOME
echo $PATH_TO_ICHOR

cd $INPUT_DIR
#ls * | grep *gz | xargs gzip -d
#extract unique names of the samples
NAMES=$(ls * --color=never | grep -P ".bam" | awk -F ".bam.bai" '{print $1}' | sort | uniq)
echo $NAMES

#execute the pipline for each sample
apply_to_each_fastq pipeline "${NAMES[@]}" ${REF_GENOME} ${HG_FASTA} ${ICHOR}



###################################################################################################
#		          INSERT SIZE DISTRIBUTION GENERATION									
###################################################################################################

for i in $NAMES; do
    picard -Xmx15g CollectInsertSizeMetrics \
    I= ${i}.markdup.bam \
    O=${i}-insert_size_metrics.txt \
    H=${i}-insert_size_histogram.pdf \
    M=0.05
done;

mkdir insert_size_distr
mv *-insert_size_* insert_size_distr

#--------------------------------------------------------------------------------------------------

