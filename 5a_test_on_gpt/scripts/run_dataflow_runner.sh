#!/bin/bash

python3 pipeline/main.py --runner DataflowRunner \
   --model_state_dict_path gs://ggml_models/gpt2_medium.pth \
   --model_name openai-community/gpt2 \
   --project long-axle-412512 \
   --region us-central1 \
   --requirements_file requirements.txt \
   --staging_location gs://dataflow-staging-europe-west2-1028464732444 \
   --temp_location gs://mypipelines-dataflow-temp/ \
   --experiments "use_runner_v2,no_use_multiple_sdk_containers" \
   --machine_type=n1-standard-96 \
   --experiments=enable_data_sampling
