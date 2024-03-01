#!/bin/bash

echo "Build Docker image"
docker build --no-cache -t whisper_pipeline -f docker/worker.Dockerfile .
echo "Tag Docker image"
docker tag whisper_pipeline europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline:latest
echo "Push Docker image"
docker push europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline:latest

echo "Build the Flex Image"
docker build --no-cache -t whisper_pipeline_flex -f docker/flex.Dockerfile .
echo "Tag Docker image"
docker tag whisper_pipeline_flex europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline_flex:latest
echo "Push Docker image"
docker push europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline_flex:latest