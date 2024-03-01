FROM nvcr.io/nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies required for Python, Beam, and GGML compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        python3-pip \
        libglib2.0-0 \
    && ln -s /usr/bin/python3.8 /usr/bin/python \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone the GGML repository and build the whisper binary
RUN git clone https://github.com/ggerganov/ggml.git /ggml \
    && cd /ggml \
    && mkdir build && cd build \
    && cmake .. \
    && make -j4 whisper
# Ensure the whisper binary is in the PATH
ENV PATH="/ggml/build/bin:${PATH}"

ARG WORKDIR=/code_pipeline/
RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}

# install python dependencies
COPY requirements.txt ${WORKDIR}/requirements.txt
COPY pipeline ${WORKDIR}/pipeline
COPY setup.py ${WORKDIR}/setup.py

RUN pip install apache-beam[gcp] \
    && pip install -r requirements.txt \
    # Download the requirements to speed up launching the Dataflow job.
    && pip download --no-cache-dir --dest /tmp/dataflow-requirements-cache -r requirements.txt \
    && pip download --no-cache-dir --dest /tmp/dataflow-requirements-cache .


ENTRYPOINT [ "/opt/apache/beam/boot" ]