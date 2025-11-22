import logging
from datetime import datetime

from airflow.sdk import dag
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

@dag(
    dag_id="city_check",
    start_date=datetime(2025, 11, 18),
    schedule='*/30 * * * *',
    catchup=False,
    description='Check the city air quality',
    tags=['city_check'],
)
def city_check():
    logger = logging.getLogger(__name__)
    logger.info("Starting create or skip cities")

    create_or_skip_cities_task = SparkSubmitOperator(
        task_id="create_or_skip_cities_task",
        application="/opt/airflow/dags/spark-jobs/create_or_skip_cities.py",
        conn_id="spark_default",
        driver_memory="2g",
        executor_memory="2g",
        verbose=True,
        packages=("org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.9.2,"
                "org.apache.iceberg:iceberg-aws-bundle:1.9.2,"
                "org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.102.5,"
                ),
        conf={},
    )

    ingest_air_quality_data_task = TriggerDagRunOperator(
        task_id="ingest_air_quality_data_task",
        trigger_dag_id="air_quality_data_ingestion",
    )

    create_or_skip_cities_task >> ingest_air_quality_data_task

city_check()
