#!/bin/bash

python3 pipeline/whisper_pipeline.py --runner DataflowRunner \
   --project long-axle-412512 \
   --region us-central1 \
   --job_name whisper-pipeline \
   --requirements_file requirements.txt \
   --staging_location gs://dataflow-staging-europe-west2-1028464732444 \
   --temp_location gs://mypipelines-dataflow-temp/ \
   --experiments "use_runner_v2,no_use_multiple_sdk_containers" \
   --machine_type=n1-highmem-16 \
   --disk_size_gb=200
