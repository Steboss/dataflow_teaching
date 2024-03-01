FROM gcr.io/dataflow-templates-base/python39-template-launcher-base:latest AS template_launcher
FROM europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline:latest

COPY --from=template_launcher /opt/google/dataflow/python_template_launcher /opt/google/dataflow/python_template_launcher


ARG WORKDIR=/code_pipeline/
RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}
# RUN apt-get update \
#     && apt-get install -y libffi-dev git \
#     && rm -rf /var/lib/apt/lists/* \
#     && pip install --upgrade pip \
#     && pip install apache-beam[gcp] \
#     && pip install -r requirements.txt \
#     # Download the requirements to speed up launching the Dataflow job.
#     && pip download --no-cache-dir --dest /tmp/dataflow-requirements-cache -r requirements.txt \
#     && pip download --no-cache-dir --dest /tmp/dataflow-requirements-cache .


# flex environment variables
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/pipeline/whisper_pipeline.py"
ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${WORKDIR}/requirements.txt"
ENV FLEX_TEMPLATE_PYTHON_SETUP_FILE="${WORKDIR}/setup.py"
ENV PIP_NO_DEPS=True

ENTRYPOINT ["/opt/google/dataflow/python_template_launcher"]
