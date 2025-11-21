import logging

from airflow.sdk import dag
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

@dag(
    dag_id="clean_raw_data",
    schedule=None,
    catchup=False,
    description="Clean raw data",
    tags=["clean", "raw", "data"],
)
def clean_raw_data():
    logger = logging.getLogger(__name__)
    logger.info("Starting clean raw data")

    clean_raw_data_task = SparkSubmitOperator(
        task_id="clean_raw_data_task",
        application="/opt/airflow/dags/spark-jobs/clean_raw_data.py",
        conn_id="spark_default",
        driver_memory="2g",
        executor_memory="2g",
        verbose=True,
    )