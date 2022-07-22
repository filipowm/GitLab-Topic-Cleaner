FROM python:3.9-alpine
ARG TOOL_PATH=/opt/gitlab-topics-cleaner

RUN mkdir ${TOOL_PATH} && apk add build-base
WORKDIR ${TOOL_PATH}
COPY ./requirements.txt ${TOOL_PATH}/requirements.txt

RUN pip install -r requirements.txt

COPY ./ /opt/gitlab-topics-cleaner

ENTRYPOINT ["python3", "/opt/gitlab-topics-cleaner/gitlab-cleaner.py"]