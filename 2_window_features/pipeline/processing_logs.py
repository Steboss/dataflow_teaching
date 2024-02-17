import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam import window
from structlog import get_logger
import json

logger = get_logger()


class ComputeMovingAverageFn(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        timestamp, values = element
        avg_value = sum(values) / len(values) if values else 0
        yield {'window': window.start, 'average': avg_value}


def run_pipeline(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-subscription', dest='input_subscription', required=True)
    parser.add_argument('--output-subscription', dest='output_subscription', required=True)
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
         | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(subscription=known_args.input_subscription)
         | 'Parse JSON' >> beam.Map(lambda x: json.loads(x))
         | 'Window into' >> beam.WindowInto(window.FixedWindows(60))  # 60-second windows
         | 'Group by Key' >> beam.GroupByKey()
         | 'Compute Moving Average' >> beam.ParDo(ComputeMovingAverageFn())
         | 'Encode JSON' >> beam.Map(lambda x: json.dumps(x).encode('utf-8'))
         | 'Write to Pub/Sub' >> beam.io.WriteToPubSub(subscription=known_args.output_subscription)
        )


if __name__ == '__main__':
    run_pipeline()
