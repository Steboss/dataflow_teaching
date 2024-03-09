#!/bin/bash

PIPELINE_NAME="window-pipeline"
PROJECT="long-axle-412512"
REGION="us-central1"
NUM_MAX_WORKERS=2

echo "Running pipeline"

python pipeline/processing_logs.py \
    --input_subscription projects/long-axle-412512/subscriptions/example-window-pipeline-sub \
    --output_topic projects/long-axle-412512/topics/example-output-window-pipeline \
    --runner DataflowRunner \
    --region ${REGION} \
    --project ${PROJECT} \
    --temp_location gs://mypipelines-dataflow-temp/ \
    --staging_location gs://dataflow-staging-europe-west2-1028464732444/ \
    --job_name ${PIPELINE_NAME}
