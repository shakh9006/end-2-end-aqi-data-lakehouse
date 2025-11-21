import logging
from airflow.sdk import dag
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

@dag(
    dag_id="air_quality_data_ingestion",
    schedule=None,
    catchup=False,
    description="Ingest air quality data",
    tags=["ingestion", "api", "air_quality"],
)
def air_quality_data_ingestion():
    logger = logging.getLogger(__name__)
    logger.info("Starting air quality data ingestion")

    ingest_raw_data_task = SparkSubmitOperator(
        task_id="ingest_raw_data_task",
        application="/opt/airflow/dags/spark-jobs/ingest_raw_data.py",
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

    trigger_clean_raw_data_task = TriggerDagRunOperator(
        task_id="trigger_clean_raw_data_task",
        trigger_dag_id="clean_raw_data",
    )

    ingest_raw_data_task >> trigger_clean_raw_data_task

air_quality_data_ingestion()