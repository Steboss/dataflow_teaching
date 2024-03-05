#!/bin/bash
echo "*************************"
echo "Build Flex Template"
gcloud dataflow flex-template build gs://flex_templates_my_pipeline/sawtooh_window_template.json \
--image-gcr-path europe-west2-docker.pkg.dev/long-axle-412512/sawtooth-window-pipeline/sawtooh_window_pipeline:latest \
--sdk-language "PYTHON" \
--metadata-file metadata/metadata.json \
--project long-axle-412512 \
--worker-region europe-west2 \
--env  "FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt" \
--env "FLEX_TEMPLATE_PYTHON_PY_FILE=pipeline/processing_logs.py" \
--env "FLEX_TEMPLATE_PYTHON_SETUP_FILE=setup.py" \
--flex-template-base-image "PYTHON3" \
--py-path "."