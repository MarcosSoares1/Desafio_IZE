
#  Desafio Engenharia de Dados — Logística

Este projeto foi desenvolvido como parte de um desafio técnico para a vaga de Engenheiro de Dados Jr. Ele simula o processamento de dados logísticos de rastreamento de pacotes, utilizando boas práticas de arquitetura em camadas (Bronze, Silver, Gold), orquestração com Airflow, persistência em PostgreSQL e visualização com Power BI.

##  Tecnologias Utilizadas

- Python + Pandas
- Airflow
- PostgreSQL
- Power BI
- Matplotlib + Seaborn (visualização exploratória)

##  Arquitetura em Camadas

- **Bronze** → Ingestão de dados brutos com rastreabilidade
- **Silver** → Limpeza, enriquecimento e particionamento por data
- **Gold** → Agregações finais, persistência em banco e visualizações

---

##  Camada Bronze — Ingestão de Dados Brutos

###  Objetivo

Armazenar os dados exatamente como foram recebidos, sem alterações, garantindo rastreabilidade, organização e escalabilidade para as próximas camadas do pipeline.

###  Estrutura de Pastas

```
Desafio_IZE/
├── dados/
│   └── rastreamento.csv
│   └── bronze/
│       ├── resultado_rastreamento_bronze.csv
│       └── metadados_YYYYMMDD_HHMMSS.json
```

###  O que o script faz

- Lê o arquivo bruto `rastreamento.csv`
- Padroniza os nomes das colunas
- Salva o CSV tratado na pasta `bronze/`
- Gera um arquivo de metadados com:
  - Caminho do arquivo
  - Camada
  - Timestamp
  - Total de linhas
  - Nome e tipo das colunas

###  Como executar

```bash
python scripts/resultado_rastreamento_bronze.py
```

---

##  Camada Silver — Processamento e Tratamento

###  Objetivo

Aplicar regras de negócio, limpar e enriquecer os dados para torná-los confiáveis e prontos para análise. Os dados são particionados por ano e mês, simulando múltiplas execuções e facilitando auditoria.

###  Estrutura de Pastas

```
Desafio_IZE/
├── dados/
│   └── silver/
│       └── ano=2025/
│           └── mes=10/
│               ├── resultado_rastreamento_silver.csv
│               └── metadados_YYYYMMDD_HHMMSS.json
```

###  O que o script faz

- Lê o arquivo da camada Bronze
- Remove duplicatas e valores nulos
- Converte `data_atualizacao` para datetime
- Cria colunas derivadas: `ano`, `mes`, `dia`, `hora`
- Valida os valores de `status_rastreamento`
- Salva o CSV tratado em partições por data
- Gera metadados atualizados, incluindo duplicatas

###  Como executar

```bash
python scripts/resultado_rastreamento_silver.py
```

---

##  Camada Gold — Armazenamento e Visualização

###  Objetivo

Persistir os dados tratados em banco de dados relacional e gerar visualizações analíticas.

###  Estrutura de Pastas

```
Desafio_IZE/
├── dados/
│   └── gold/
│       ├── resultado_rastreamento_gold.csv
│       └── metadados_YYYYMMDD_HHMMSS.json
```

###  O que o script faz

- Lê o arquivo mais recente da camada Silver
- Realiza agregações e análises (ex: total por status, volume por cidade)
- Exporta os dados finais para PostgreSQL
- Salva o CSV final na pasta `gold/`
- Gera metadados finais

###  Como executar

```bash
python scripts/resultado_rastreamento_gold.py
```

---

##  Visualizações com Python — Explorando a Camada Gold

Além da integração com Power BI, foram desenvolvidas visualizações exploratórias com Python utilizando as bibliotecas `matplotlib` e `seaborn`. Essa etapa não era obrigatória no desafio, mas foi implementada como diferencial técnico.

### Gráficos gerados:

- **Gráfico de Barras — Número de Pacotes por Status Final**  
  Representa a distribuição dos pacotes entre os status `sucesso`, `falha` e `pendente`.

- **Gráfico de Linha — Volume de Envios por Dia**  
  Exibe a quantidade de pacotes movimentados por dia, com correção de datas para evitar sobreposição entre meses e anos.

- **Gráfico de Linha — Volume de Envios por Data Completa**  
  Utiliza a composição de `ano`, `mes` e `dia` para gerar uma linha do tempo precisa, permitindo identificar tendências e picos de movimentação.

###  Como executar

```bash
python scripts/visualizacao_gold.py
```

Os gráficos serão salvos automaticamente na pasta `dados/gold/` como arquivos `.png`.

---

##  Modelo Relacional — Desafio 1, Questão 2

```sql
CREATE TABLE Pacotes (
  id_pacote VARCHAR PRIMARY KEY,
  origem TEXT,
  destino TEXT
);

CREATE TABLE EventosRastreamento (
  id_evento SERIAL PRIMARY KEY,
  id_pacote VARCHAR REFERENCES Pacotes(id_pacote),
  status_rastreamento TEXT,
  data_atualizacao TIMESTAMP
);
```

###  Justificativa

- Permite múltiplos eventos por pacote, refletindo o histórico completo
- Facilita consultas analíticas (tempo médio, status atual)
- Garante integridade referencial
- Escalável para grandes volumes e integração futura com APIs

---

##  Justificativa das Tecnologias — Desafio 1, Questão 3

- **Python + Pandas**: manipulação rápida e eficiente de dados tabulares
- **PostgreSQL**: banco relacional robusto e compatível com BI
- **Power BI**: visualização interativa e acessível
- **Airflow**: orquestração confiável e escalável para pipelines em produção

> Ferramentas como Spark ou Dataflow foram consideradas desnecessárias para o volume atual.

---

##  Desafio 2 — Monitoramento e Eficiência Logística

###  Questão 1 — Dashboard em Tempo Quase Real

Foi proposta uma solução com:

- Ingestão via Airflow agendado
- Processamento incremental com scripts Python
- Armazenamento em PostgreSQL
- Visualização com Power BI

####  Métricas simuladas:

- Número de pacotes por status
- Média de tempo de entrega (via SQL)
- Volume por origem/destino

---

###  Questão 2 — Adaptação para Ingestão via API

Embora não implementado, foi documentado um esboço de arquitetura futura:

####  Mudanças necessárias:

- Substituir leitura de CSV por API (FastAPI, Kafka)
- Processamento em tempo real
- Persistência incremental
- Validação e ordenação dos dados

####  Modelo adaptado:

Cada evento vira uma linha com timestamp, mantendo histórico completo.

####  Arquitetura proposta:

```
[API de rastreamento] → [Kafka/FastAPI] → [Spark Streaming] → [PostgreSQL] → [Power BI]
```

---

##  Observações Finais

Este pipeline foi desenvolvido com foco em:

-  Boas práticas de engenharia de dados
-  Escalabilidade e modularidade
-  Rastreabilidade via metadados
-  Visualização clara e objetiva dos dados logísticos
