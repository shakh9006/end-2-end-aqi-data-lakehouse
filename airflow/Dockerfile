FROM apache/airflow:3.1.2

COPY requirements.txt /requirements.txt

USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    net-tools \
    iputils-ping \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y openjdk-17-jre-headless procps && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER airflow

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt