# Example Dockerfile (adjust as needed)
FROM gcr.io/dataflow-templates-base/python3-template-launcher-base

# Install Whisper and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    git

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
