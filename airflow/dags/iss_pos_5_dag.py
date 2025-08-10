import urllib3
import json
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.operators.http import SimpleHttpOperator


@dag(
    schedule_interval=timedelta(minutes=15),
    start_date=datetime(2025, 1, 1),
    catchup=False,
)


def iss_position_tracking_5():
    
    create_iss_position_table = PostgresOperator(
        task_id="create_iss_position_table",
        postgres_conn_id="pgsql",
        sql="""
            CREATE TABLE IF NOT EXISTS public.iss_position (
            latitude float4 NOT NULL,
            longitude float4 NOT NULL,
            message varchar NOT NULL,
            pos_timestamp int4 PRIMARY KEY);
            """
    )

    @task()
    def download_iss_position():
        http = urllib3.PoolManager()
        url = 'http://api.open-notify.org/iss-now.json'
        response = http.request('GET', url)
        obj = json.loads(response.data.decode('utf-8'))
        #
        result = dict()
        iss = obj["iss_position"]
        result["latitude"] = iss["latitude"]
        result["longitude"] = iss["longitude"]
        result["message"] = obj["message"]
        result["pos_timestamp"] = obj["timestamp"]
        return result

    @task()
    def load(**context):
        lat = context["ti"].xcom_pull(task_ids='download_iss_position', key='latitude')
        lon = context["ti"].xcom_pull(task_ids='download_iss_position', key='longitude')
        message = context["ti"].xcom_pull(task_ids='download_iss_position', key='message')
        pos_timestamp = context["ti"].xcom_pull(task_ids='download_iss_position', key='pos_timestamp')
         
        sql1 = 'INSERT INTO public.iss_position (latitude, longitude, message, pos_timestamp) '
        sql2 = f"VALUES({lat},{lon},'{message}',{pos_timestamp});"
        sql_text = sql1 + sql2

        PostgresOperator(
            task_id="insert_data_to_db",
            postgres_conn_id="pgsql",
            sql=sql_text,
            # """
            #     INSERT INTO public.iss_position (latitude, longitude, message, pos_timestamp)
            #     VALUES( 
            #             {{ params.latitude }}, 
            #             {{ params.longitude }}, 
            #             '{{ params.message }}', 
            #             {{ params.pos_timestamp }}
            #     );
            #     """,
            # params={
            #     'latitude': context["ti"].xcom_pull(task_ids='download_iss_position', key='latitude') }}",
            #     'longitude': context["ti"].xcom_pull(task_ids='download_iss_position', key='longitude') }}",
            #     'message': context["ti"].xcom_pull(task_ids='download_iss_position', key='message') }}",
            #     'pos_timestamp': context["ti"].xcom_pull(task_ids='download_iss_position', key='pos_timestamp') }}"
            # }
        )

    # выполняем цепочку задач
    create_iss_position_table >> download_iss_position() >> load()


dag = iss_position_tracking_5()