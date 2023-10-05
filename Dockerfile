FROM python:3.12

RUN pip install deflacue

COPY convert.py convert.py

