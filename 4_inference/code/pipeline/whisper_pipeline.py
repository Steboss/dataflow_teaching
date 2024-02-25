import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from structlog import get_logger
import subprocess
import json

logger = get_logger()


class GGMLModelInferenceFn(beam.DoFn):
    """ Apache Beam DoFn for invoking the GGML model inference using the whisper command-line tool."""
    def setup(self):
        """ Set up the model binary path."""
        self.model_binary_path = 'gs://ggml_models/ggml-model.bin'

    def process(self, element):
        input_file = 'gs://input_files_my_pipeline/sampled_16khz.wav' # sysargv[1]
        output_file = 'gs://input_files_my_pipeline/test_output.json' # sysargv[2]
        language = 'italian'

        # Construct the whisper command
        cmd = [
            'whisper',
            '-m', self.model_binary_path,
            '-f', input_file,
            '-oj', output_file,
            '-l', language
        ]

        # Execute whisper command
        subprocess.run(cmd, check=True)

        # do we need this?
        # Load and yield the output from whisper
        with open(output_file, 'r') as f:
            output_data = json.load(f)
            yield output_data


def run_pipeline(argv=None):
    parser = argparse.ArgumentParser()
    # input files, we can read from a bucket extracting all the files
    # now just test with 16khz
    # parser.add_argument('--input-bucket-path', dest='input_files', required=True)
    # parser.add_argument('--output-bucket-path', dest='output_files', required=True)
    parser.add_argument('--job_name', dest='job_name', required=True)
    parser.add_argument('--project', dest='project', required=True)
    parser.add_argument('--region', dest='region', required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(
        pipeline_args,
        streaming=True,
        save_main_session=True,
        job_name=known_args.job_name,
        project=known_args.project,
        region=known_args.region
    )

    with beam.Pipeline(options=pipeline_options) as p:
        (p
         | 'Model Inference' >> beam.ParDo(GGMLModelInferenceFn())
         )


if __name__ == '__main__':
    run_pipeline()
