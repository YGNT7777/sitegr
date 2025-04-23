# Use an official Python runtime as a parent image
FROM python:3.9-slim

RUN pip install --no-cache-dir requests

WORKDIR /github/workspace

ENTRYPOINT ["python", ".github/actions/check-sensitive-files/check.py"]
