FROM gcr.io/dataflow-templates-base/python39-template-launcher-base AS template_launcher
FROM europe-west2-docker.pkg.dev/long-axle-412512/whisper-pipeline/whisper_pipeline:latest

COPY --from=template_launcher /opt/google/dataflow/python_template_launcher /opt/google/dataflow/python_template_launcher

RUN apt-get install -y python3.9 python3-pip \
    && ln -s $(which python3.9) /usr/local/bin/python

RUN apt-get -y install git cmake python3-pip
# download ggml and install whisper
RUN git clone https://github.com/ggerganov/ggml.git \
    && cd ggml \
    && mkdir build && cd build \
    && cmake .. \
    && make -j4 whisper

ARG WORKDIR=/dataflow/template
RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}
RUN mv /code_pipeline/* ${WORKDIR}
ENV PATH="/dataflow/template/ggml/build/bin:${PATH}"
# flex environment variables
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/pipeline/whisper_pipeline.py"
ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${WORKDIR}/requirements.txt"
ENV FLEX_TEMPLATE_PYTHON_SETUP_FILE="${WORKDIR}/setup.py"
ENV PIP_NO_DEPS=True

ENTRYPOINT ["/opt/google/dataflow/python_template_launcher"]