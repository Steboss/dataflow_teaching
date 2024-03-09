#!/bin/bash

echo "Build Docker image"
docker build --no-cache -t sawtooh_window_pipeline -f docker/Dockerfile .
echo "Tag Docker image"
docker tag sawtooh_window_pipeline europe-west2-docker.pkg.dev/long-axle-412512/sawtooth-window-pipeline/sawtooh_window_pipeline:latest
echo "Push Docker image"
docker push europe-west2-docker.pkg.dev/long-axle-412512/sawtooth-window-pipeline/sawtooh_window_pipeline:latest
