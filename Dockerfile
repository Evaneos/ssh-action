FROM python:3.8.0-alpine3.10

RUN apk add --no-cache ca-certificates \
  openssh-client \
  sshpass \
  knock

COPY requirements.txt /requirements.txt

RUN apk add --no-cache --virtual .build-deps build-base musl-dev libffi-dev openssl-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /requirements.txt \
    && apk del .build-deps

COPY ssh /action/ssh

ENV PYTHONPATH /action
ENTRYPOINT [ "python", "/action/ssh/main.py" ]
