import logging
import sys
from datetime import datetime

sys.path.append('/opt/airflow/project_config')


from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


from project_config.config import DEFAULT_ARGS

def test_dag_handler():
    logging.info('Test DAG!!!')

dag = DAG(
    dag_id='test_dag',
    default_args=DEFAULT_ARGS,
    start_date=datetime(2025, 9, 4),
    schedule='0 0 * * *',
    catchup=False,
    description='Test DAG',
    tags=['test'],
    max_active_runs=1,
    max_active_tasks=1,
)

with dag:

    start = EmptyOperator(task_id='start')

    python_operator = PythonOperator(task_id='python_operator', python_callable=test_dag_handler)

    end = EmptyOperator(task_id='end')

    (
        start >>
        python_operator >>
        end
    )