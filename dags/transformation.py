import logging

from airflow.sdk import dag
from custom_operator.dbt_operator import DbtCoreOperator
from airflow import settings

DBT_PROJECT_PATH = f"{settings.DAGS_FOLDER}/dbt_trino"

@dag(
    dag_id="transformation",
    schedule=None,
    catchup=False,
    description="Transformation",
    tags=["transformation"],
)
def transformation():
    logger = logging.getLogger(__name__)
    logger.info("Starting transformation")

    dbt_task = DbtCoreOperator(
        task_id='dbt_task',
        dbt_project_dir=DBT_PROJECT_PATH,
        dbt_profiles_dir=DBT_PROJECT_PATH,
        dbt_command='run',
    )

    dbt_task

transformation()