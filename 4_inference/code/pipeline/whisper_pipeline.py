import subprocess
import json
import tempfile
from typing import Iterable, Optional, Dict, Any
from apache_beam.ml.inference.base import RunInference
from apache_beam.ml.inference.base import ModelHandler
from apache_beam.ml.inference.base import PredictionResult
from google.cloud import storage
from apache_beam.options.pipeline_options import PipelineOptions
from structlog import get_logger
import apache_beam as beam
import argparse
import os


logger = get_logger()


class GGMLModelHandler(ModelHandler[str, PredictionResult, str]):
    def __init__(self, model_gcs_path: str, language: str = "Italian"):
        """Implementation of the ModelHandler interface for GGML Whisper model using audio files as input.

        Example Usage::

          pcoll | RunInference(GGMLModelHandler(model_gcs_path="gs://ggml_models/ggml-model.bin"))

        Args:
          model_gcs_path: The GCS path to the Whisper model binary file.
          language: The language for the Whisper model. Default is English.
        """
        self.model_gcs_path = model_gcs_path
        self.language = language
        self._env_vars = {}
        self.model_temp_file = None

    def load_model(self) -> str:
        """Loads and initializes a model for processing."""
        # Split the GCS path to bucket name and blob name
        gcs_path_parts = self.model_gcs_path.replace("gs://", "").split("/")
        bucket_name = gcs_path_parts[0]
        model_blob_name = "/".join(gcs_path_parts[1:])

        # Initialize Google Cloud Storage client
        client = storage.Client()

        # Create a temporary file to store the downloaded model
        self.model_temp_file = tempfile.NamedTemporaryFile(delete=False)

        # Download the model file from GCS to the temporary file
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(model_blob_name)
        blob.download_to_filename(self.model_temp_file.name)

        return self.model_temp_file.name

    def run_inference(
        self,
        batch: Iterable[str],  # Batch of GCS paths to WAV files
        model: str,
        inference_args: Optional[Dict[str, Any]] = None
    ) -> Iterable[PredictionResult]:
        """Runs inferences on a batch of audio files.

        Args:
          batch: A sequence of GCS paths to WAV files.
          model: The path to the local Whisper model file.
          inference_args: Any additional arguments for inference.

        Returns:
          An Iterable of type PredictionResult.
        """
        predictions = []
        for wav_gcs_path in batch:
            # Construct the command for Whisper inference
            cmd = [
                'whisper',
                '-m', model,
                '-f', wav_gcs_path,
                '-l', self.language,
                '-oj', 'transcribed.json',
                '--duration', '60000'
            ]

            # Execute the Whisper command and capture the output
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            predictions.append(result.stdout)

        # Convert JSON strings to PredictionResult objects
        return [PredictionResult(wav_gcs_path, json.loads(prediction)) for wav_gcs_path, prediction in zip(batch, predictions)]

    def cleanup(self):
        """Cleanup temporary files and resources."""
        if self.model_temp_file:
            self.model_temp_file.close()
            os.unlink(self.model_temp_file.name)

    def validate_inference_args(self, inference_args: Optional[Dict[str, Any]] = None):
        # Validate any additional arguments for inference here.
        # For now, we'll pass as there are no additional args required.
        pass

    def get_preprocess_fns(self):
        """Returns preprocessing functions, if any."""
        # Since no preprocessing is required, return a pass-through function
        def preprocess_fn(element):
            return element
        return [preprocess_fn]


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
    pipeline_options = PipelineOptions(
        pipeline_args,
        streaming=False,
        save_main_session=True,
        job_name=known_args.job_name,
        project=known_args.project,
        region=known_args.region
    )

    with beam.Pipeline(options=pipeline_options) as p:
        result = (p
                  | 'Match Audio Files' >> beam.Create(['gs://input_files_my_pipeline/sampled_16khz.wav'])
                  | 'Model Inference' >> RunInference(model_handler=GGMLModelHandler(model_gcs_path="gs://ggml_models/ggml-model.bin", language="italian"))
                  | 'Print mode' >> beam.Map(print)
                  )


if __name__ == '__main__':
    run_pipeline()
