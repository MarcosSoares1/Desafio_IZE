## 🥉 Camada Bronze — Dados brutos e ingestão

### Objetivo:
#Armazenar os dados **exatamente como foram recebidos**, sem alterações.

### Boas práticas:
#- ✅ **Ingestão fiel**: não alterar os dados originais.
#- 📁 **Separar por fonte e data**: organizar por partições (ex: `fonte=data_source/ano=2025/mes=10`).
#- 🧾 **Registrar metadados**: como número de registros, colunas, formato, origem.
#- 🔐 **Auditoria e rastreabilidade**: salvar duplicatas, erros e logs de ingestão.
#- 🧼 **Evitar pré-tratamentos**: apenas limpeza mínima (ex: padronização de colunas).


import pandas as pd 
import os 
from datetime import datetime
from utils import salvar_metadados
import sys 


sys.path.append("/opt/airflow/dags/scripts")
from utils import salvar_metadados

# Caminho ingestão dos dados
base_dir = os.path.dirname(os.path.abspath(__file__))
caminho_csv = os.path.join(base_dir, "..", "dados", "rastreamento.csv")

# verifica se existe csv e tratamento de erros
try: 
    track_data = pd.read_csv(caminho_csv)
    print("Ingestao realizada com sucesso!")
except FileNotFoundError:
     raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")
except pd.errors.ParserError:
    raise FileNotFoundError(f"Erro ao interpretar o CSV: {caminho_csv}")

# padronização de colunas (removendo os espaços em branco - convertendo todos os nomes das colunas em minuscula)
# * dessa forma podemos evitar erros futuros em filtros e joins
track_data.columns = track_data.columns.str.strip().str.lower()

# criando a pasta para salvar os dados
pasta_bronze = "/opt/airflow/dados/bronze"
os.makedirs(pasta_bronze, exist_ok=True)

caminho_saida = os.path.join(pasta_bronze, "resultado_rastreamento_bronze.csv")

# salvar arquivo na camada bronze para continuar o tratamento
track_data.to_csv(caminho_saida, index=False)

# criando função com timestamp gerando nome unico de arquivo
# Criando função para salvar metadados --pensado em organização, escalabilidade e rastreamento
# utilizando utils.py

salvar_metadados(track_data, caminho_saida, "bronze")
print(f"Arquivo salvo em: {caminho_saida}")
