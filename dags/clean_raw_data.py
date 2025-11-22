import logging

from airflow.sdk import dag
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

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

    trigger_dbt_task = TriggerDagRunOperator(
        task_id="trigger_dbt_task",
        trigger_dag_id="dbt_trino",
    )

    clean_raw_data_task >> trigger_dbt_task

clean_raw_data()