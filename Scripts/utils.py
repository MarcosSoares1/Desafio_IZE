import os
import json
from datetime import datetime
import pandas as pd
import unicodedata

def gerar_timestamp():
    """Gera um timestamp único para versionamento de arquivos."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def salvar_metadados(track_data: pd.DataFrame, caminho_csv: str, camada: str):
    """Gera e salva metadados de um DataFrame em formato JSON."""
    metadados = {
        "caminho_arquivo": caminho_csv,
        "camada": camada,
        "timestamp": gerar_timestamp(),
        "total_linhas": len(track_data),
        "colunas": list(track_data.columns),
        "tipos_dados": track_data.dtypes.astype(str).to_dict(),
        "data_processamento": datetime.now().isoformat()
    }
    pasta = os.path.dirname(caminho_csv)
    os.makedirs(pasta, exist_ok=True)
    caminho_json = os.path.join(pasta, f"metadados_{metadados['timestamp']}.json")
    with open(caminho_json, "w") as z:
        json.dump(metadados, z, indent=4)
    print(f"[INFO] Metadados salvos em: {caminho_json}")

def salvar_metadados_com_duplicatas(track_data_limpo: pd.DataFrame, track_data_duplicado: pd.DataFrame, pasta_destino: str, camada: str):
    """Salva metadados incluindo informações sobre duplicatas."""
    timestamp = gerar_timestamp()
    metadados = {
        "camada": camada,
        "timestamp": timestamp,
        "total_linhas": len(track_data_limpo) + len(track_data_duplicado),
        "duplicatas": len(track_data_duplicado),
        "linhas_validas": len(track_data_limpo),
        "colunas": list(track_data_limpo.columns),
        "tipos_dados": track_data_limpo.dtypes.astype(str).to_dict(),
        "data_processamento": datetime.now().isoformat()
    }
    os.makedirs(pasta_destino, exist_ok=True)
    caminho_json = os.path.join(pasta_destino, f"metadados_{timestamp}.json")
    with open(caminho_json, "w") as z:
        json.dump(metadados, z, indent=4)
    print(f"[INFO] Metadados com duplicatas salvos em: {caminho_json}")


def normalizar_texto(texto: str) -> str:
    """Remove acentuação, converte para minúsculo e elimina espaços extras."""
    if not isinstance(texto, str):
        return texto
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('utf-8')
    return texto.strip().lower()
