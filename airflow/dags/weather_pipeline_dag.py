from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

default_args = {
    'owner': 'weather-pipeline',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'email_on_failure': False,
}

with DAG(
    dag_id='weather_pipeline',
    default_args=default_args,
    description='Fetch weather data → Kafka → S3',
    start_date=datetime(2024, 1, 1),
    schedule_interval='*/15 * * * *',  # Every 15 minutes
    catchup=False,
    tags=['weather', 'kafka', 's3'],
) as dag:

    # Task 1 — Fetch weather and publish to Kafka
    fetch_and_stream = BashOperator(
        task_id='fetch_and_stream_to_kafka',
        bash_command='python /opt/airflow/kafka/producer.py',
    )

    # Task 2 — Read from Kafka and save to S3
    consume_to_s3 = BashOperator(
        task_id='consume_kafka_to_s3',
        bash_command='python /opt/airflow/kafka/consumer.py',
    )

    # Task 1 runs first, then Task 2
    fetch_and_stream >> consume_to_s3