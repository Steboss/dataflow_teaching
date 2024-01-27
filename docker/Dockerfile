FROM apache/beam_python3.10_sdk:2.53.0

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip

# Run processing_logs.py when the container launches
ENTRYPOINT ["/opt/apache/beam/boot"]