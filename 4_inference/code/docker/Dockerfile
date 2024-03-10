FROM gcr.io/dataflow-templates-base/python38-template-launcher-base

ENV DEBIAN_FRONTEND=noninteractive
# Install Whisper and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    make

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

# Set the entrypoint
ENTRYPOINT ["/opt/apache/beam/boot"]
