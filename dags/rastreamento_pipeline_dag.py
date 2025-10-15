from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.task_group import TaskGroup
from datetime import datetime
import os

# 📦 Funções de execução de cada camada
def run_bronze():
    os.system("python /opt/airflow/scripts/resultado_rastreamento_bronze.py")

def run_silver():
    os.system("python /opt/airflow/scripts/resultado_rastreamento_silver.py")

def run_gold():
    os.system("python /opt/airflow/scripts/resultado_rastreamento_gold.py")

# 🗓️ Definição da DAG
with DAG(
    dag_id="pipeline_rastreamento",
    description="Pipeline de ingestão e tratamento de dados logísticos com sensor e TaskGroups",
    start_date=datetime(2025, 10, 11),
    schedule_interval="@daily",
    catchup=False,
    tags=["rastreamento", "bronze", "silver", "gold"]
) as dag:

    # 🔍 Sensor: aguarda arquivo rastreamento.csv
    sensor_arquivo = FileSensor(
        task_id="aguarda_arquivo_rastreamento",
        filepath="/opt/airflow/dados/rastreamento.csv",
        poke_interval=30,
        timeout=600
    )

    # 🥉 TaskGroup Bronze
    with TaskGroup("bronze_etapas") as bronze_group:
        bronze_ingestao = PythonOperator(
            task_id="bronze_ingestao",
            python_callable=run_bronze
        )

    # 🥈 TaskGroup Silver
    with TaskGroup("silver_etapas") as silver_group:
        silver_tratamento = PythonOperator(
            task_id="silver_tratamento",
            python_callable=run_silver
        )

    # 🥇 TaskGroup Gold
    with TaskGroup("gold_etapas") as gold_group:
        gold_analise = PythonOperator(
            task_id="gold_analise_final",
            python_callable=run_gold
        )

    # 🔗 Orquestração
    sensor_arquivo >> bronze_group >> silver_group >> gold_group