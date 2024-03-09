import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.userstate import BagStateSpec, CombiningValueStateSpec, ReadModifyWriteStateSpec

from apache_beam import window
from structlog import get_logger
from datetime import datetime
import json

logger = get_logger()


class CountSuccessFailure(beam.CombineFn):
    def create_accumulator(self):
        return {'success': 0, 'fail': 0}

    def add_input(self, accumulator, input):
        if input['event_type'] == 'success':
            accumulator['success'] += 1
        else:
            accumulator['failure'] += 1
        return accumulator

    def merge_accumulators(self, accumulators):
        merged = self.create_accumulator()
        for acc in accumulators:
            merged['success'] += acc['success']
            merged['failure'] += acc['failure']
        return merged

    def extract_output(self, accumulator):
        return accumulator


def key_by_user_window(element, window=beam.DoFn.WindowParam):
    user_id = element['user_id']
    # Use window's start as part of the key (as an example)
    window_start = window.start.micros
    key = (user_id, window_start)
    return key, 1


def run_pipeline(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-subscription', dest='input_subscription', required=True)
    parser.add_argument('--output-topic', dest='output_topic', required=True)
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
        windowed_elements = (
            p
            | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(subscription=known_args.input_subscription)
            | 'Parse JSON' >> beam.Map(lambda x: json.loads(x))
            | 'Extract Timestamp' >> beam.Map(lambda x: beam.window.TimestampedValue(x, datetime.strptime(x['timestamp'], "%Y%m%d%H%M%S").timestamp()))
            | 'Fixed Window Test' >> beam.WindowInto(beam.window.FixedWindows(60)) # here we are gathering elements in a 60 seconds windows
            | 'Key By User ID' >> beam.Map(lambda x: (x['user_id'], x['event_type']))
            | 'Count Success/Failure' >> beam.CombinePerKey(CountSuccessFailure())
            | 'Print Results' >> beam.Map(print)
        )

        # | 'Extract Timestamp' >> beam.Map(lambda x: beam.window.TimestampedValue(x, datetime.strptime(x['timestamp'], "%Y%m%d%H%M%S").timestamp()))


        result = p.run()
        result.wait_until_finish()


        # what if we want to do more? --> pardo function to associate multiple windows

        # exmaple of output out of parse json
        #({'timestamp': '20240306133453', 'user_id': 'user_0', 'event_type': 'success', 'source_ip': '192.1.1.2'},
        #1709730326.152, (GlobalWindow,), PaneInfo(first: True, last: True, timing: UNKNOWN, index: 0, nonspeculative_index: 0))

        # timestamps output
        #({'timestamp': '20240306141824', 'user_id': 'user_4', 'event_type': 'success', 'source_ip': '192.1.4.2'}, 1709734704.0, (GlobalWindow,), PaneInfo(first: True, last: True, timing: UNKNOWN, index: 0, nonspeculative_index: 0))

        # element to windo
        #([1709734700.0, 1709734720.0), 1709734704.0, (GlobalWindow,), PaneInfo(first: True, last: True, timing: UNKNOWN, index: 0, nonspeculative_index: 0))


if __name__ == '__main__':
    run_pipeline()
