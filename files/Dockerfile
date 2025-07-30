FROM oraclelinux:8.6

RUN dnf -y install wget bzip2 && dnf clean all

ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p $CONDA_DIR && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    conda clean -afy

RUN conda tos accept --yes --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --yes --channel https://repo.anaconda.com/pkgs/r

RUN conda create -n tso500_archiving -y -c bioconda -c conda-forge samtools && \
    conda clean -afy

SHELL ["/bin/bash", "-c"]
RUN echo "source activate tso500_archiving" >> ~/.bashrc

CMD ["/bin/bash"]
