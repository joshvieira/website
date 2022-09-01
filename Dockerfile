FROM continuumio/miniconda3:latest

# Create the conda environment:
COPY cfg/conda.yml /tmp/
RUN conda env create -f /tmp/conda.yml

# Install tmux
RUN apt-get update && apt install -y tmux

# Create the root project directory
# Using VOLUME vs COPY so changes to code base will not require recreating the whole image
ENV WORKDIR=/website
RUN mkdir -p $WORKDIR
VOLUME $WORKDIR

# Activate virtual environment on login
RUN echo "source activate webenv" > ~/.bashrc
ENV PATH /opt/conda/envs/webenv/bin:$PATH
ENV PYTHONPATH "${PYTHONPATH}:${WORKDIR}"

WORKDIR $WORKDIR