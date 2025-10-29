# Use a ready-to-go Miniconda base image
FROM continuumio/miniconda3:latest

# Everything is expected to be mounted at /mnt/code when you run the container
WORKDIR /mnt/

# Copy the env spec into the image so we can build at image build time
# (Assumes ichorCNA.yaml is next to this Dockerfile when you build)
COPY ichorCNA.yaml /tmp/ichorCNA.yaml

# Create the conda env
RUN conda env create -f /tmp/ichorCNA.yaml && conda clean -afy

# Make "conda activate" work in RUN/CMD
SHELL ["/bin/bash", "-lc"]

# Auto-activate the env for interactive shells
RUN echo "conda activate TSO500ichorCNA" >> ~/.bashrc

# Allow overriding paths at runtime via ENV (relative to /mnt/code)
ENV ICHOR_SCRIPT="tso500_dragen_pipeline/sandbox/ichorCNA_docker/tso500offtarget_ichorcna/drv_TSO500_offtarget_ichorCNA_parallel.sh" \
    DATA_DIR="tso500_dragen_pipeline/sandbox/ichorCNA_docker/data" \
    ICHOR_DIR="tso500_dragen_pipeline/ichorCNA"
