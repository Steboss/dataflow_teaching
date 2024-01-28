FROM gcr.io/dataflow-templates-base/python39-template-launcher-base:20230622_RC00

WORKDIR /app
COPY pipeline /app/pipeline
COPY requirements.txt /app/requirements.txt
COPY setup.py /app/setup.py


ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${WORKDIR}/requirements.txt"
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/pipeline/processing_logs.py"
ENV FLEX_TEMPLATE_PYTHON_SETUP_FILE="${WORKDIR}/setup.py"

RUN apt-get update \
    && apt-get install -y libffi-dev git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install apache-beam[gcp] \
    && pip install -r $FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE \
    # Download the requirements to speed up launching the Dataflow job.
    && pip download --no-cache-dir --dest /tmp/dataflow-requirements-cache -r $FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE \
    && pip download --no-cache-dir --dest /tmp/dataflow-requirements-cache .

RUN python setup.py install

ENV PIP_NO_DEPS=True