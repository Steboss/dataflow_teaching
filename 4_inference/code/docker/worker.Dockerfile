FROM nvcr.io/nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04

# Set the entrypoint to Apache Beam SDK worker launcher.
COPY --from=apache/beam_python3.9_sdk:2.46.0 /opt/apache/beam /opt/apache/beam


ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get dist-upgrade -y \
    && apt-get install -y --no-install-recommends --fix-missing build-essential libncurses5-dev libgdbm-dev libnss3-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev zlib1g-dev libssl-dev liblzma-dev default-libmysqlclient-dev g++ curl \
    && apt-get -y install git cmake python3-pip

ARG WORKDIR=/code_pipeline/
RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}
# download ggml and install whisper
RUN git clone https://github.com/ggerganov/ggml.git \
    && cd ggml \
    && mkdir build && cd build \
    && cmake .. \
    && make -j4 whisper
# MAKE SURE WHISPER IS PRESENT!
# install python dependencies
COPY requirements.txt ${WORKDIR}/requirements.txt
RUN pip install -r ${WORKDIR}/requirements.txt

COPY pipeline ${WORKDIR}/pipeline
COPY setup.py ${WORKDIR}/setup.py
ENV PYTHONPATH ${WORKDIR}

ENTRYPOINT [ "/opt/apache/beam/boot" ]