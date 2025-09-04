FROM apache/airflow:3.0.2

COPY requirements.txt /requirements.txt

USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt

# Copy any additional files if needed (uncomment as needed)
# COPY ./dags /opt/airflow/dags
# COPY ./plugins /opt/airflow/plugins
# COPY ./config /opt/airflow/config