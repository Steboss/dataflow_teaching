FROM gcr.io/dataflow-templates-base/python39-template-launcher-base:latest AS template_launcher
FROM europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline:latest

COPY --from=template_launcher /opt/google/dataflow/python_template_launcher /opt/google/dataflow/python_template_launcher

ARG WORKDIR=/code_pipeline/
RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}
# flex environment variables
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/pipeline/whisper_pipeline.py"
ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${WORKDIR}/requirements.txt"
ENV FLEX_TEMPLATE_PYTHON_SETUP_FILE="${WORKDIR}/setup.py"
ENV PIP_NO_DEPS=True

ENTRYPOINT ["/opt/google/dataflow/python_template_launcher"]
