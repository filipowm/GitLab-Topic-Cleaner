FROM python:3.9-alpine
ARG TOOL_PATH=/opt/gitlab-topics-cleaner

RUN echo 'alias cleaner="python ${TOOL_PATH}/cli.py"' >> ~/.bashrc
RUN mkdir ${TOOL_PATH} && apk add build-base
WORKDIR ${TOOL_PATH}
COPY ./requirements.txt ${TOOL_PATH}/requirements.txt

RUN pip install -r requirements.txt

COPY ./ /opt/gitlab-topics-cleaner

ENTRYPOINT ['cleaner']