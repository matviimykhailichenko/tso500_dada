# Base image with Oracle Linux 8.6
FROM oraclelinux:8.6

# Install dependencies for Conda and samtools
RUN dnf -y install wget bzip2 && dnf clean all

# Install Miniconda (lightweight version of Anaconda)
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p $CONDA_DIR && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    conda clean -afy

# Create a new environment and install latest samtools
RUN conda create -n tso500_archiving -y -c bioconda -c conda-forge samtools && \
    conda clean -afy

# Activate the environment in bash
SHELL ["/bin/bash", "-c"]
RUN echo "source activate tso500_archiving" >> ~/.bashrc

# Default command
CMD ["/bin/bash"]
