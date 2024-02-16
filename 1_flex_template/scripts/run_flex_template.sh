#!/bin/bash

PIPELINE_NAME="processing-pipeline"
PROJECT="long-axle-412512"
DATAFLOW_GCS_LOCATION="gs://flex_templates_my_pipeline/template.json"
NUM_MAX_WORKERS=2

echo "Running Flex Template"
gcloud dataflow flex-template run ${PIPELINE_NAME} \
--project=${PROJECT} \
--template-file-gcs-location=${DATAFLOW_GCS_LOCATION} \
--worker-region=us-central1 \
--region=us-central1 \
--worker-machine-type=n1-standard-2 \
--max-workers=$NUM_MAX_WORKERS  \
--num-workers=1  \
--temp-location=gs://mypipelines-dataflow-temp/ \
--staging-location=gs://dataflow-staging-europe-west2-1028464732444/ \
--parameters job_name=processing-pipeline \
--parameters project=${PROJECT} \
--parameters region=us-central1 \
--parameters input-file=gs://input_files_my_pipeline/input_file.txt \
--parameters output-file=gs://input_files_my_pipeline/output
