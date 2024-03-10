#!/bin/bash

echo "Build Docker image"
docker build --no-cache -t europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline:latest -f docker/Dockerfile .
echo "Push Docker image"
docker push europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline:latest