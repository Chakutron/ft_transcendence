FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /transcendence

RUN apt update && apt upgrade -y

COPY requirements.txt .
COPY manage.py .
COPY certs/ certs/

RUN python3 -m venv venv
RUN venv/bin/pip3 install --upgrade pip
RUN venv/bin/pip3 install --no-cache-dir -r requirements.txt -v

EXPOSE 8080
