import pandas as pd
import sqlalchemy
import os
import sys
import logging
from datetime import datetime
from utils import gerar_timestamp, salvar_metadados

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Caminho base
base_dir = os.path.dirname(os.path.abspath(__file__))
silver_base = os.path.join(base_dir, "..", "dados", "silver")

# Localiza partição mais recente
anos = sorted(os.listdir(silver_base), reverse=True)
for ano in anos:
    ano_path = os.path.join(silver_base, ano)
    if os.path.isdir(ano_path):
        meses = sorted(os.listdir(ano_path), reverse=True)
        for mes in meses:
            mes_path = os.path.join(ano_path, mes)
            if os.path.isdir(mes_path):
                caminho_entrada = os.path.join(mes_path, "resultado_rastreamento_silver.csv")
                if os.path.exists(caminho_entrada):
                    break
        else:
            continue
        break
else:
    raise FileNotFoundError("Nenhuma partição válida encontrada na camada Silver.")

logging.info(f"Lendo arquivo da Silver: {caminho_entrada}")

# Cria pasta Gold
pasta_gold = os.path.join(base_dir, "..", "dados", "gold")
os.makedirs(pasta_gold, exist_ok=True)

# Leitura dos dados
track_data = pd.read_csv(caminho_entrada)
track_data["data_atualizacao"] = pd.to_datetime(track_data["data_atualizacao"]).dt.tz_localize(None)

# Classificação de status
def classificar_status(status):
    if status == "entregue":
        return "sucesso"
    elif status in ["extraviado", "cancelado"]:
        return "falha"
    else:
        return "pendente"

track_data["status_final"] = track_data["status_rastreamento"].apply(classificar_status)

# Agregações
volume_por_origem = track_data.groupby("origem").size().reset_index(name="volume_envios")
track_data = track_data.merge(volume_por_origem, on="origem", how="left")
track_data["hora_minuto"] = track_data["data_atualizacao"].dt.strftime("%H:%M")
track_data = track_data.sort_values(by=["data_atualizacao", "origem"])
track_data.columns = track_data.columns.str.lower().str.replace(" ", "_")

# Reordenar colunas
colunas_ordenadas = [
    "id_pacote", "origem", "destino", "status_rastreamento", "status_final",
    "data_atualizacao", "ano", "mes", "dia", "hora_minuto", "volume_envios"
]
track_data = track_data[colunas_ordenadas]

# Salvamento final
caminho_saida = os.path.join(pasta_gold, "resultado_rastreamento_gold.csv")
track_data.to_csv(caminho_saida, index=False)
logging.info(f"Arquivo salvo em: {caminho_saida}")

# Metadados
salvar_metadados(track_data, caminho_saida, "gold")
logging.info(f"Total de registros processados: {len(track_data)}")

# Exportação para PostgreSQL
engine = sqlalchemy.create_engine("postgresql://airflow:airflow@postgres:5432/rastreamento")
track_data.to_sql("rastreamento_gold", engine, if_exists="replace", index=False)
logging.info("Dados salvos no PostgreSQL com sucesso.")