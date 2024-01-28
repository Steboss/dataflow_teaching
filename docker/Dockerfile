FROM apache/beam_python3.10_sdk:2.53.0

WORKDIR /app
COPY pipeline /app/pipeline
COPY requirements.txt requirements.txt


RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run processing_logs.py when the container launches
CMD ["python", "-m", "pipeline.processing_logs"]