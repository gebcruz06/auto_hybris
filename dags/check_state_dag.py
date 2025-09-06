from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

from scripts.test_browser import test_browser
from scripts.extract_hybris import extract_hybris
from scripts.get_my_ip import get_my_ip

import pendulum

with DAG(
    dag_id='check_state_dag',
    start_date=pendulum.datetime(2024, 7, 3, tz='Asia/Singapore'),
    tags = ['manual', 'python', 'testing'],
    schedule_interval=None,
    catchup=False,
) as dag:
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')
    test_browser_task = PythonOperator(
        task_id='test_browser',
        python_callable=test_browser,
        show_return_value_in_logs=True
    )
    get_my_ip_task = PythonOperator(
        task_id='get_my_ip',
        python_callable=get_my_ip,
        show_return_value_in_logs=True
    )
    extract_hybris_task = PythonOperator(
        task_id='extract_hybris',
        python_callable=extract_hybris,
        show_return_value_in_logs=True
    )

    start >> test_browser_task >> get_my_ip_task >> extract_hybris_task >> end

    