import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from structlog import get_logger
import time

logger = get_logger()


class ParseLogEntry(beam.DoFn):
    def process(self, element):
        # Assuming log entries are in CSV format: timestamp,event_type,duration
        timestamp, event_type, duration = element.split(',')
        return [{'event_type': event_type, 'duration': float(duration)}]


class CalculateAverageDuration(beam.CombineFn):
    def create_accumulator(self):
        return (0.0, 0)

    def add_input(self, accumulator, input):
        total_duration, count = accumulator
        for duration in input:
            total_duration += duration
            count += 1
        return total_duration, count

    def merge_accumulators(self, accumulators):
        total_duration, count = zip(*accumulators)
        return sum(total_duration), sum(count)

    def extract_output(self, accumulator):
        total_duration, count = accumulator
        return total_duration / count if count != 0 else 0


def run_pipeline(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', dest='input', required=True)
    parser.add_argument('--output-file', dest='output', required=True)
    parser.add_argument('--job_name', dest='job_name', required=True)
    parser.add_argument('--project', dest='project', required=True)
    parser.add_argument('--temp_location', dest='temp_location', required=True)
    parser.add_argument('--region', dest='region', required=True)
    parser.add_argument('--staging_location', dest='staging_location', required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(
        pipeline_args,
        streaming=False,
        save_main_session=True,
        job_name=known_args.job_name,
        project=known_args.project,
        temp_location=known_args.temp_location,
        region=known_args.region,
        staging_location=known_args.staging_location
    )

    with beam.Pipeline(options=pipeline_options) as pipeline:
        results = (
            pipeline
            | 'ReadFromText' >> beam.io.ReadFromText(known_args.input)
            | 'ParseLogEntry' >> beam.ParDo(ParseLogEntry())
            | 'WithKeys' >> beam.Map(lambda element: (element['event_type'], element['duration']))
            | 'GroupByKey' >> beam.GroupByKey()
            | 'CalculateAverageDuration' >> beam.CombinePerKey(CalculateAverageDuration())
            | 'FormatOutput' >> beam.Map(lambda kv: f'Event Type: {kv[0]}, Average Duration: {kv[1]:.2f}')
            | 'WriteToText' >> beam.io.WriteToText(known_args.output)
        )

    #current_running_pipe = pipeline.run()
    #current_running_pipe.wait_until_finish()


if __name__ == '__main__':
    start_time = time.time()
    run_pipeline()
    end_time = time.time()
    logger.info(f"Total time {end_time - start_time}")
