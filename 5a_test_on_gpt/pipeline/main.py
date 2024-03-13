import argparse
import sys
import logging
import apache_beam as beam
from apache_beam.ml.inference.base import RunInference
from apache_beam.ml.inference.pytorch_inference import PytorchModelHandlerTensor
from apache_beam.ml.inference.pytorch_inference import make_tensor_model_fn
from apache_beam.options.pipeline_options import PipelineOptions
from transformers import AutoConfig
from transformers import GPT2LMHeadModel, GPT2Tokenizer


class Preprocess(beam.DoFn):

    def __init__(self, tokenizer: GPT2Tokenizer):
        self._tokenizer = tokenizer

    def process(self, element):
        """
          Process the raw text input to a format suitable for GPTJ

          Args:
            element: A string of text

          Returns:
            A tokenized example
        """
        input_ids = self._tokenizer(
            element, return_tensors="pt").input_ids.to('cpu')
        return input_ids


class Postprocess(beam.DoFn):
    def __init__(self, tokenizer: GPT2Tokenizer):
        self._tokenizer = tokenizer

    def process(self, element):
        """
          Process the PredictionResult to print the translated texts

          Args:
            element: The RunInference output to be processed.
        """
        logging.info(f"Input postprocess element {element}")
        decoded_inputs = self._tokenizer.decode(
            element.example, skip_special_tokens=True)
        decoded_outputs = self._tokenizer.decode(
            element.inference, skip_special_tokens=True)
        logging.info(f"{decoded_inputs} \t Output: {decoded_outputs}")
        print(f"{decoded_inputs} \t Output: {decoded_outputs}")


def parse_args(argv):
    """Parses args for the workflow."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_state_dict_path",
        dest="model_state_dict_path",
        required=True,
        help="Path to the model's state_dict.",
    )
    parser.add_argument(
        "--model_name",
        dest="model_name",
        required=False,
        help="Path to the model's state_dict.",
        default="t5-small",
    )

    return parser.parse_known_args(args=argv)


def run():
    """
    Runs the interjector pipeline which translates English sentences
    into German using the RunInference API.
    """

    known_args, pipeline_args = parse_args(sys.argv)
    pipeline_options = PipelineOptions(pipeline_args)

    gen_fn = make_tensor_model_fn('generate')

    model_handler = PytorchModelHandlerTensor(
        state_dict_path=known_args.model_state_dict_path,
        model_class=GPT2LMHeadModel,
        model_params={"config": AutoConfig.from_pretrained("gpt2")},
        device="cpu",
        inference_fn=gen_fn,
        inference_args={"min_length":1024, "max_length":2048,}
    )

    input_prompts = [
        "summarize: Mi rivolgo a chi vuole un po' di buonsenso, una giustizia che difende gli aggrediti e non gli aggressori, uno Stato che permette di andare in pensione dopo 41 anni aprendo il mondo del lavoro ai nostri giovani, una burocrazia che lascia lavorare serenamente gli imprenditori, una società più sicura per i nostri figli, un Paese dove le culle tornano a riempirsi.",
        "summarize: Mi rivolgo a chi vuole un po' di buonsenso, una giustizia che difende gli aggrediti e non gli aggressori, uno Stato che permette di andare in pensione dopo 41 anni aprendo il mondo del lavoro ai nostri giovani, una burocrazia che lascia lavorare serenamente gli imprenditori, una società più sicura per i nostri figli, un Paese dove le culle tornano a riempirsi.",
        "summarize: Mi rivolgo a chi vuole un po' di buonsenso, una giustizia che difende gli aggrediti e non gli aggressori, uno Stato che permette di andare in pensione dopo 41 anni aprendo il mondo del lavoro ai nostri giovani, una burocrazia che lascia lavorare serenamente gli imprenditori, una società più sicura per i nostri figli, un Paese dove le culle tornano a riempirsi.",
        "summarize: Buonsenso è cancellare la Legge Fornero!Insieme ai lavoratori delle acciaierie di Piombino.",
        "summarize: Buonsenso è cancellare la Legge Fornero!Insieme ai lavoratori delle acciaierie di Piombino.",
        "continue: Buonsenso è cancellare la Legge Fornero!Insieme ai lavoratori delle acciaierie di Piombino."
    ]

    tokenizer = GPT2Tokenizer.from_pretrained(known_args.model_name)

    # [START Pipeline]
    with beam.Pipeline(options=pipeline_options) as pipeline:
        _ = (
            pipeline
            | "CreateInputs" >> beam.Create(input_prompts)
            | "Preprocess" >> beam.ParDo(Preprocess(tokenizer=tokenizer))
            | "RunInference" >> RunInference(model_handler=model_handler)
            | "PostProcess" >> beam.ParDo(Postprocess(tokenizer=tokenizer))
            | "Print" >> beam.Map(print)
        )

    # [END Pipeline]


if __name__ == "__main__":
    run()
