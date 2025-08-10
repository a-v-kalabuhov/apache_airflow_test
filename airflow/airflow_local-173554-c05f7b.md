## Запускаем Airflow локально

1. Docker в РФ:
https://habr.com/ru/articles/818527/
или
https://tproger.ru/articles/docker-hub-v-rossii---vse--gajd--kak-obojti-blokirovku

2. curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.5/docker-compose.yaml'
   Добавляем name: 'airflow' перед Services

3. Устанавливаем docker и docker-compose плагин

4. touch .env 
   
5. vi .env 
   export AIRFLOW_UID=50000

6. docker-compose up

7. Заходим на http://127.0.0.1:8080
Логин и пароль: airflow

8. Поработаем с starting_dag.py и после найдем 'my_very_own_etl' DAG в UI
9. Изменим парамент AIRFLOW__CORE__LOAD_EXAMPLES: 'true' в docker-compose.yaml и перезапустим все

10. Остановим контейнеры: docker-compose down

11. Чтобы установить доп пакеты, нужно заменить 
  image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.10.5} в docker-compose.yaml на
  build: . 
  и создать в этой же папке 
  requirements.txt и Dockerfile

12. Dockerfile:
    FROM apache/airflow:2.10.5
    ADD requirements.txt .
    RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt 