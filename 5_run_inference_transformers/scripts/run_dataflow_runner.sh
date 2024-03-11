#!/bin/bash 

python3 pipeline/main.py --runner DataflowRunner \
   --model_state_dict_path gs://ggml_models/gptj.pth \
   --model_name "EleutherAI/gpt-j-6B" \
   --project long-axle-412512 \
   --region us-central1 \
   --requirements_file requirements.txt \
   --staging_location gs://dataflow-staging-europe-west2-1028464732444 \
   --temp_location gs://mypipelines-dataflow-temp/ \
   --experiments "use_runner_v2,no_use_multiple_sdk_containers" \
   --machine_type=n1-highmem-16 \
   --disk_size_gb=200
