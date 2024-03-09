import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.userstate import BagStateSpec, CombiningValueStateSpec, ReadModifyWriteStateSpec

from apache_beam import window
from structlog import get_logger
from datetime import datetime
import json

logger = get_logger()


class AssignToSawtoothWindow(beam.DoFn):
    def process(self, element, timestamp=beam.DoFn.TimestampParam):
        # Example sawtooth pattern: 10s, 20s, 30s windows, then reset
        window_sizes = [10, 20, 30]  # Window sizes in seconds
        epoch_time = int(timestamp)
        cycle_period = sum(window_sizes)
        cycle_position = epoch_time % cycle_period

        # Determine the current window size based on cycle_position
        accumulator = 0
        for size in window_sizes:
            accumulator += size
            if cycle_position < accumulator:
                current_window_size = size
                break

        # Calculate the window start and end times
        window_start = epoch_time - (epoch_time % current_window_size)
        window_end = window_start + current_window_size
        yield beam.window.IntervalWindow(window_start, window_end)


def key_by_user_window(element, window=beam.DoFn.WindowParam):
    user_id = element['user_id']  # Or use 'source_ip' for grouping by IP
    return ((window, user_id), 1)


class SumSuccessFailure(beam.DoFn):
    def process(self, element):
        # element[0] is the user_id, element[1] is an iterable of events
        user_id, events = element
        success_count = sum(1 for event in events if event['event_type'] == 'success')
        failure_count = sum(1 for event in events if event['event_type'] == 'fail')
        yield user_id, {'success': success_count, 'fail': failure_count}



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
            | 'Assign elements within a sawtooth window' >> beam.ParDo(AssignToSawtoothWindow())
            | 'Key By User and Window' >> beam.ParDo(key_by_user_window)  # Pass the entire event dictionary as value
            | 'Group By User ID' >> beam.GroupByKey()
            | 'Sum Success/Failure' >> beam.ParDo(SumSuccessFailure())
            | 'Print final results' >> beam.Map(print)
        )



        result = p.run()
        result.wait_until_finish()


if __name__ == '__main__':
    run_pipeline()
