import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configurações visuais
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# Caminho para o arquivo Gold
base_dir = os.path.dirname(os.path.abspath(__file__))
caminho_gold = os.path.join(base_dir, "..", "dados", "gold", "resultado_rastreamento_gold.csv")

# Verifica se o arquivo existe
if not os.path.exists(caminho_gold):
    raise FileNotFoundError(f"Arquivo nao encontrado: {caminho_gold}")

# Carrega os dados
track_data = pd.read_csv(caminho_gold)

# Gráfico 1 — Barras: número de pacotes por status_final
plt.figure()
sns.countplot(data=track_data, x="status_final", palette="viridis")
plt.title("Numero de Pacotes por Status Final")
plt.xlabel("Status Final")
plt.ylabel("Quantidade")
plt.tight_layout()
plt.savefig(os.path.join(base_dir, "..", "dados", "gold", "grafico_status_final.png"))
plt.close()

# Gráfico 2 — Linha: volume de envios por data 

track_data["data"] = pd.to_datetime({
    "year": track_data["ano"],
    "month": track_data["mes"],
    "day": track_data["dia"]
})
envios_por_data = track_data.groupby("data").size().reset_index(name="volume")

plt.figure()
sns.lineplot(data=envios_por_data, x="data", y="volume", marker="o", color="darkorange")
plt.title("Volume de Envios por Data Completa")
plt.xlabel("Data")
plt.ylabel("Volume")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(base_dir, "..", "dados", "gold", "grafico_envios_por_data.png"))
plt.close()

print("Todos os graficos foram gerados e salvos na pasta gold.")