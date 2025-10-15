
# Etapas no script Silver
#- Ler o arquivo da camada Bronze
#- Tratar nulos em campos textuais
#- Identificar e salvar duplicatas
#- Remover duplicatas
#- Converter tipos de dados
#- Validar status logístico
#- Criar colunas derivadas
#- Salvar CSV tratado
#- Gerar metadados com duplicatas via utils.py

import pandas as pd 
import os
from datetime import datetime 
import sys
import json
from utils import gerar_timestamp, salvar_metadados, salvar_metadados_com_duplicatas, normalizar_texto

# Ingestão para a camada silver
sys.path.append("/opt/airflow/scripts")
base_dir = os.path.dirname(os.path.abspath(__file__))
caminho_entrada = os.path.join(base_dir, "..", "dados", "bronze", "resultado_rastreamento_bronze.csv")

# verifica se o arquivo existe 
if not os.path.exists(caminho_entrada):
    raise FileNotFoundError(f"Arquivo de entrada não encontrado: {caminho_entrada}")


pasta_silver = os.path.join(base_dir, "..", "dados", "silver")
os.makedirs(pasta_silver, exist_ok=True)

track_data = pd.read_csv(caminho_entrada)



# Analisando uma ingestão com milhoes de linhas, pode realizar a extração de duplicidades(linhas)
# A melhor forma de fazer garantido a confiabilidade e a rastreabilidade, e tambem depois fornecer os dados
# duplicados, para realizar uma analise de qualidade do 'por que' estes dados estão se repetindo, pensando nisso
# estou salvando os dados em uma outra tabela duplicados_track_data e evita decisões irreversiveis

# Salvar duplicatas para auditoria
duplicados_track_data = track_data[track_data.duplicated()]
track_data = track_data.drop_duplicates()

salvar_metadados_com_duplicatas(track_data, duplicados_track_data, pasta_silver, "silver")

# removendo colunas vazias (Nesse caso especifico não existe, mas pensado em bigdata)
track_data = track_data.dropna(axis=1, how="all")

# convertendo os tipos de dados
#print(track_date.info())# verificando quais
track_data["data_atualizacao"] = pd.to_datetime(track_data["data_atualizacao"], errors="coerce")
track_data["origem"] = track_data["origem"].astype(str)
track_data["destino"] = track_data["destino"].astype(str)
track_data["status_rastreamento"] = track_data["status_rastreamento"].astype(str)

erros_data = track_data["data_atualizacao"].isna().sum()
print(f"Registros com data invalidas: {erros_data}")

# normalização de texto e tem o tratamento com valores nulos 
campos_textuais = ["origem", "destino", "status_rastreamento"]
for coluna in campos_textuais:
    if coluna in track_data.columns:
        track_data[coluna] = track_data[coluna].fillna("não informado")
        track_data[coluna] = track_data[coluna].apply(normalizar_texto)

## verificando se a conversão para (datetime) deu 'erro' em algum registro
## print(track_data["data_atualizacao"].isna().sum())

# validação de status
status_validos = [
    "em transito", "entregue", "extraviado", "em rota de entrega",
    "aguardando retirada", "cancelado"
]
track_data = track_data[track_data["status_rastreamento"].isin(status_validos)]

# colunas derivadas
track_data["ano"] = track_data["data_atualizacao"].dt.year
track_data["mes"] = track_data["data_atualizacao"].dt.month
track_data["dia"] = track_data["data_atualizacao"].dt.day
track_data["hora"] = track_data["data_atualizacao"].dt.hour

# particionamento por data -- 
ano = f"ano={track_data['ano'].iloc[0]}"
mes = f"mes={track_data['mes'].iloc[0]:02d}"
pasta_silver = os.path.join(base_dir, "..", "dados", "silver", ano, mes)
os.makedirs(pasta_silver, exist_ok=True)


# salvando o csv para a etapa gold
caminho_saida = os.path.join(pasta_silver, "resultado_rastreamento_silver.csv")
track_data.to_csv(caminho_saida, index=False)
print(f"Arquivo salvo em: {caminho_saida}")
