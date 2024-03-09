import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.fileio import MatchFiles, ReadMatches
import tempfile
from structlog import get_logger
import subprocess
import json
from datetime import datetime
from google.cloud import storage
import os


logger = get_logger()

# USE A CUSTOM HANDLER FOR THIS FUNCTION
class GGMLModelInferenceFn(beam.DoFn):
    """ Apache Beam DoFn for invoking the GGML model inference using the whisper command-line tool."""
    # def setup(self):
    #     """ Set up the model binary path."""
    #     self.model_binary_path = 'gs://ggml_models/ggml-model.bin'
    def start_bundle(self):
        # Initialize Google Cloud Storage client
        self.client = storage.Client()

        # Name of the bucket and object (model file)
        bucket_name = 'ggml_models'
        model_blob_name = 'ggml-model.bin' # whisper model

        # Create a temporary file to store the downloaded model
        self.model_temp_file = tempfile.NamedTemporaryFile(delete=False)

        # Download the model file from GCS to the temporary file
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(model_blob_name)
        blob.download_to_filename(self.model_temp_file.name)

        # Now self.model_temp_file.name contains the path to the downloaded model file
        # You can use this path in the process method for inference

    def process(self, element):
        with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
            # Read the content from the ReadableFile and write it to the temporary file
            with element.open() as f:
                temp_audio_file.write(f.read())
        #input_file = element #'gs://input_files_my_pipeline/sampled_16khz.wav' # sysargv[1]
        output_file = 'test_output.json' # sysargv[2]
        language = 'italian'

        # Construct the whisper command
        cmd = [
            'whisper',
            '-m', self.model_temp_file.name,
            '-f', temp_audio_file.name,
            '-l', language,
            '-oj'
        ]
        #➜ build/bin/whisper -m ../ggml_whisper/output_ggml_model/ggml-model.bin -f ../ggml_whisper/sampled_16khz.wav -l italian -nt -d 60000 -otxt
        # the output is in the folder of the file

        # Execute whisper command
        subprocess.run(cmd, check=True)

        # do we need this?
        # Load and yield the output from whisper
        with open(output_file, 'r') as f:
            output_data = json.load(f)
            yield output_data

    def finish_bundle(self):
        # Clean up the temporary file
        os.remove(self.model_temp_file.name)


def run_pipeline(argv=None):
    parser = argparse.ArgumentParser()
    # input files, we can read from a bucket extracting all the files
    # now just test with 16khz
    #parser.add_argument('--input-wav-file', dest='input_file', required=True)
    # parser.add_argument('--output-bucket-path', dest='output_files', required=True)
    parser.add_argument('--job_name', dest='job_name', required=True)
    parser.add_argument('--project', dest='project', required=True)
    parser.add_argument('--region', dest='region', required=True)

    known_args, pipeline_args = parser.parse_known_args(argv)
    dataflow_options = {"streaming": False,
                        "save_main_session": True,
                        "job_name": f"{known_args.job_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "project": known_args.project,
                        "region": known_args.region,
                        "sdk_container_image": 'europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline_flex:latest',
                        }
    flags = ["--experiment=worker_accelerator=type:nvidia-tesla-p4;count:1;install-nvidia-driver"],
    options = PipelineOptions(flags=flags, **dataflow_options)

    with beam.Pipeline(options=options) as p:
        result = (p
                  | 'Match Audio Files' >> MatchFiles('gs://input_files_my_pipeline/sampled_16khz.wav')
                  | 'Read Matches' >> ReadMatches()
                  | 'Model Inference' >> beam.ParDo(GGMLModelInferenceFn())
                  )


if __name__ == '__main__':
    run_pipeline()
