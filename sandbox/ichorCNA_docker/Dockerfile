FROM oraclelinux:8.6

# Install required system dependencies
RUN dnf -y install wget bzip2 rsync which && \
    dnf clean all

# Install Miniconda
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    $CONDA_DIR/bin/conda clean -afy

# Accept ToS and create environment
RUN $CONDA_DIR/bin/conda config --set always_yes yes && \
    $CONDA_DIR/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    $CONDA_DIR/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r && \
    $CONDA_DIR/bin/conda create --name ichorCNA && \
    $CONDA_DIR/bin/conda clean -afy

RUN conda config --set solver classic
RUN conda config --add channels bioconda
RUN conda config --add channels conda-forge
RUN conda config --add channels r
RUN conda config --add channels biobuilds
RUN conda config --add channels defaults

RUN conda config --set solver classic && \
    conda install -y hmmcopy picard samtools bwa r-rcurl r-ragg libxml2 && \
    conda clean -afy
