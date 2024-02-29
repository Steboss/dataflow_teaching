#!/bin/bash

PIPELINE_NAME="whisper-pipeline"
PROJECT="long-axle-412512"
REGION="europe-west1"
DATAFLOW_GCS_LOCATION="gs://flex_templates_my_pipeline/whisper_template.json"
NUM_MAX_WORKERS=10

echo "Running Flex Template"
gcloud dataflow flex-template run ${PIPELINE_NAME} \
--project=${PROJECT} \
--template-file-gcs-location=${DATAFLOW_GCS_LOCATION} \
--worker-region=${REGION} \
--region=${REGION} \
--worker-machine-type=n4-standard-2 \
--max-workers=$NUM_MAX_WORKERS  \
--num-workers=5  \
--temp-location=gs://mypipelines-dataflow-temp/ \
--staging-location=gs://dataflow-staging-europe-west2-1028464732444/ \
--worker_harness_container_image="europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline_flex:latest" \
--parameters job_name=window-pipeline \
--parameters project=${PROJECT} \
--parameters region=${REGION} \
--parameters disk_size_gb=50 \
--parmaeters dataflow_service_options="worker_accelerator=type:nvidia-tesla-t4;count:1;install-nvidia-driver" \
--parameters dataflow_service_options="worker_harness_container_image=europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline_flex:latest"