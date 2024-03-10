#!/bin/bash

PIPELINE_NAME="whisper-pipeline"
PROJECT="long-axle-412512"
REGION="us-central1"
#NUM_MAX_WORKERS=2
HOME="/home/sbosisio486/dataflow_teaching/4_inference/code"

echo "Installing requirements"
sudo pip uninstall --yes -r requirements.txt
sudo pip install -r requirements.txt

echo "MAKE SURE TO EXPORT YOU GOOGLE APPLICTION CREDENTIALS IF IN C.E"

echo "Running pipeline"

python3 pipeline/whisper_pipeline.py --runner DataflowRunner \
   --project ${PROJECT} \
   --region ${REGION} \
   --job_name ${PIPELINE_NAME} \
   --requirements_file requirements.txt \
   --staging_location gs://dataflow-staging-europe-west2-1028464732444 \
   --temp_location gs://mypipelines-dataflow-temp/ \
   --experiments "use_runner_v2,no_use_multiple_sdk_containers" \
   --machine_type=n1-highmem-16 \
   --disk_size_gb=200 \
    --experiments=enable_data_sampling
