import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.typehints import Tuple, Any, KV
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
            | 'Timestamps' >> beam.Map(lambda x: beam.window.TimestampedValue(x, datetime.strptime(x['timestamp'], "%Y%m%d%H%M%S").timestamp()))
            | 'Assign elements within a sawtooth window' >> beam.ParDo(AssignToSawtoothWindow())
            # Ensure you apply windowing here. If AssignToSawtoothWindow() doesn't directly apply windowing, you'll need to adjust.
        )

        failed_login_counts = (
            windowed_elements
            | 'Filter Failures' >> beam.Filter(lambda x: x['event_type'] == 'fail')
            | 'Key By User and Window' >> beam.ParDo(key_by_user_window)
            | 'Count Failures Per User Per Window' >> beam.CombinePerKey(sum)
            | 'Print' >> beam.Map(print)
        )
        result = p.run()
        result.wait_until_finish()


        # exmaple of output out of parse json
        #({'timestamp': '20240306133453', 'user_id': 'user_0', 'event_type': 'success', 'source_ip': '192.1.1.2'},
        #1709730326.152, (GlobalWindow,), PaneInfo(first: True, last: True, timing: UNKNOWN, index: 0, nonspeculative_index: 0))

        # timestamps output
        #({'timestamp': '20240306141824', 'user_id': 'user_4', 'event_type': 'success', 'source_ip': '192.1.4.2'}, 1709734704.0, (GlobalWindow,), PaneInfo(first: True, last: True, timing: UNKNOWN, index: 0, nonspeculative_index: 0))

        # element to windo
        #([1709734700.0, 1709734720.0), 1709734704.0, (GlobalWindow,), PaneInfo(first: True, last: True, timing: UNKNOWN, index: 0, nonspeculative_index: 0))


if __name__ == '__main__':
    run_pipeline()
