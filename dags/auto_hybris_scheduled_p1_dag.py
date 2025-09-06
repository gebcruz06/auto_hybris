from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum

from scripts.extract_selenium import extract_hybris
from scripts.upload_extract import upload_extract_p1
from scripts.delete_extract import delete_extract_p1

with DAG(
    dag_id='auto_hybris_scheduled_dag_p1',
    start_date=pendulum.datetime(2024, 8, 6, 15, 30, tz='Asia/Singapore'),
    tags = ['hybris', 'python', 'scheduled'],
    schedule_interval='10 15 * * *',
    catchup=False,
) as dag:
    extract_selenium_task_p1 = PythonOperator(
        task_id='extract_selenium_p1',
        python_callable=extract_hybris,
        show_return_value_in_logs=True
    )
    upload_extract_task = PythonOperator(
        task_id='upload_extract',
        python_callable=upload_extract_p1,
        show_return_value_in_logs=True
    )
    delete_extract_task = PythonOperator(
        task_id='delete_extract',
        python_callable=delete_extract_p1,
        show_return_value_in_logs=True
    )

    extract_selenium_task_p1 >> upload_extract_task >> delete_extract_task
