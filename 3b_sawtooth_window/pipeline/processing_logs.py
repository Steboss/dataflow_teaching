import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.userstate import BagStateSpec, CombiningValueStateSpec, ReadModifyWriteStateSpec

from apache_beam import window
from structlog import get_logger
from datetime import datetime
import json

logger = get_logger()


# Anomaly Detection Process (for 30s window)
class DetectAnomalies(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        user_id, events = element
        # Simple anomaly detection logic (example: high number of failed logins)
        failure_count = sum(1 for event in events if event['event_type'] == 'fail')
        if failure_count > 5:  # Threshold for anomaly
            yield user_id, {'window': window, 'anomaly': True, 'failures': failure_count}

# Moving Average Calculation (for 60s sliding window)
class CalculateMovingAverage(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        user_id, events = element
        total_successes = sum(1 for event in events if event['event_type'] == 'success')
        average = total_successes / len(events) if events else 0
        yield user_id, {'window': window, 'moving_average': average}

# Total Sum Aggregation (for 180s sliding window)
class CalculateTotalSum(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        user_id, events = element
        total_events = len(events)
        yield user_id, {'window': window, 'total_events': total_events}



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
        parsed_events = (
            p
            | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(subscription=known_args.input_subscription)
            | 'Parse JSON' >> beam.Map(lambda x: json.loads(x))
            | 'Extract Timestamp' >> beam.Map(lambda x: beam.window.TimestampedValue(x, datetime.strptime(x['timestamp'], "%Y%m%d%H%M%S").timestamp()))
        )

        # for window_duration in [30, 60, 180]:
        #     windowed_events = (
        #         parsed_events
        #         | f'Fixed Window {window_duration}s' >> beam.WindowInto(beam.window.FixedWindows(window_duration))
        #         | f'Key By User ID {window_duration}s' >> beam.Map(lambda x: (x['user_id'], x))
        #         | f'Group By User ID {window_duration}s' >> beam.GroupByKey()
        #         | f'Sum Success/Failure {window_duration}s' >> beam.ParDo(SumSuccessFailure())
        #         | 'Print' >> beam.Map(print)
        #     )
        # Short-term window (e.g., 30s fixed)
        short_term_window = (
            parsed_events
            | '30s Fixed Window' >> beam.WindowInto(beam.window.FixedWindows(30))
            | 'Key By User ID for Anomalies' >> beam.Map(lambda x: (x['user_id'], x))
            | 'Group By User ID for Anomalies' >> beam.GroupByKey()
            | 'Detect Anomalies' >> beam.ParDo(DetectAnomalies())
        )

        # Medium-term sliding window overlapping with short-term (e.g., 60s sliding, every 30s)
        medium_term_window = (
            parsed_events
            | '60s Sliding Window Every 30s' >> beam.WindowInto(beam.window.SlidingWindows(60, 30))
            | 'Key By User ID for Moving Averages' >> beam.Map(lambda x: (x['user_id'], x))
            | 'Group By User ID for Moving Averages' >> beam.GroupByKey()
            | 'Calculate Moving Average' >> beam.ParDo(CalculateMovingAverage())
        )

        # Long-term sliding window overlapping with both (e.g., 180s sliding, every 60s)
        long_term_window = (
            parsed_events
            | '180s Sliding Window Every 60s' >> beam.WindowInto(beam.window.SlidingWindows(180, 60))
            | 'Key By User ID for Total Sums' >> beam.Map(lambda x: (x['user_id'], x))
            | 'Group By User ID for Total Sums' >> beam.GroupByKey()
            | 'Calculate Total Sum' >> beam.ParDo(CalculateTotalSum())
        )

        ((short_term_window, medium_term_window, long_term_window)
            | 'Flatten Results' >> beam.Flatten()
            | 'Format for Output' >> beam.Map(lambda x: json.dumps(x).encode('utf-8'))
            | 'Write to PubSub' >> beam.io.WriteToPubSub(topic=known_args.output_topic)
        )



        result = p.run()
        result.wait_until_finish()


if __name__ == '__main__':
    run_pipeline()
