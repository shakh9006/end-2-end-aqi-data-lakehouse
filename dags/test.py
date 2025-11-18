import logging
import sys
from datetime import datetime

from airflow.sdk import dag, task

@dag(
    dag_id='test_dag',
    start_date=datetime(2025, 11, 18),
    schedule='0 0 * * *',
    catchup=False,
    description='Test DAG',
    tags=['test'],
)
def test_dag():
    @task
    def test_task():
        logging.info('Test Task!!!')
        return 'Test Task!!!'

    test_task()

test_dag()