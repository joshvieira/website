FROM continuumio/miniconda3:latest

# Create the environment:
COPY ./cfg/conda.yml ./cfg/conda.yml
RUN conda env create -f cfg/conda.yml

# Copy all files from cwd of host folder
COPY . .

# Activate virtual environment on login
RUN echo "source activate webenv" > ~/.bashrc
ENV PATH /opt/conda/envs/webenv/bin:$PATH
ENV PYTHONPATH "${PYTHONPATH}:."
