# Start from Miniconda base image (lightweight)
FROM continuumio/miniconda3

# Optional: update conda first
RUN conda update -n base -c defaults conda -y

# Install packages into base environment directly
RUN conda install -y \
    python=3.12 \
    pyyaml \
    requests \
    filelock \
    pandas

# Ensure future commands use conda's base env
SHELL ["/bin/bash", "-c"]

# Optionally initialize conda (if needed for interactive use)
RUN conda init bash

# Set the default command to bash
CMD ["bash"]