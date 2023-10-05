FROM python:3.12

RUN apt-get update
RUN apt-get -y install ffmpeg

RUN pip install deflacue

COPY convert.py convert.py
