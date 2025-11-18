FROM apache/spark:3.5.2-python3

USER root

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    net-tools \
    iputils-ping \
    vim && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/spark/ && chown -R spark:spark /home/spark/

RUN curl -fsSL -o /tmp/miniforge.sh \
    https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh && \
    bash /tmp/miniforge.sh -b -p /opt/conda && rm /tmp/miniforge.sh && \
    /opt/conda/bin/conda create -y -p /opt/conda/envs/py312 python=3.12.11 && \
    /opt/conda/bin/conda clean -afy

ENV PATH=/opt/conda/envs/py312/bin:/opt/conda/bin:$PATH
ENV PYSPARK_PYTHON=/opt/conda/envs/py312/bin/python

RUN mkdir -p /opt/spark/events && mkdir -p /opt/spark/jars/iceberg \
    && cd /opt/spark/jars/iceberg \
    && wget -q https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.9.2/iceberg-spark-runtime-3.5_2.12-1.9.2.jar \
    && wget -q https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/1.9.2/iceberg-aws-bundle-1.9.2.jar \
    && wget -q https://repo1.maven.org/maven2/org/projectnessie/nessie-integrations/nessie-spark-extensions-3.5_2.12/0.102.5/nessie-spark-extensions-3.5_2.12-0.102.5.jar \
    && wget -q https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.33.11/bundle-2.33.11.jar \
    && wget -q https://repo1.maven.org/maven2/software/amazon/awssdk/s3/2.33.11/s3-2.33.11.jar \
    && wget -q https://repo1.maven.org/maven2/software/amazon/awssdk/url-connection-client/2.33.11/url-connection-client-2.33.11.jar \
    && wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.6/hadoop-aws-3.3.6.jar \
    && cp *.jar /opt/spark/jars/ && chown -R spark:spark /opt/spark/jars/

RUN pip3 install --no-cache-dir pyspark==3.5.2

USER spark

EXPOSE 4040