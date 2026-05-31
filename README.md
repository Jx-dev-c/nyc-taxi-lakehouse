# NYC Taxi Lakehouse

Pipeline de dados local com arquitetura lakehouse em três camadas, usando DuckDB, dbt e Python.

Dataset: NYC TLC Yellow Taxi Trips (Janeiro 2023) — ~3 milhões de corridas.

---

## Arquitetura

```
raw/         → dado bruto preservado (Parquet, imutável)
trusted/     → dado limpo e validado (sem regra de negócio)
refined/     → modelos dbt materializados (DuckDB)
```

A separação de camadas não é estética — é funcional. Se uma regra de negócio muda, reprocesso a partir da trusted sem re-ingerir. Se a fonte muda schema, o impacto fica isolado na camada raw → trusted.

---

## Stack

| Camada | Tecnologia | Decisão |
|---|---|---|
| Ingestão | Python + requests | Sem overhead de framework para download simples |
| Armazenamento | Parquet | Colunar, comprimido, legível por qualquer engine |
| Transformação | Python + pandas | Validações técnicas pré-dbt |
| Modelagem | dbt Core | Versionamento, testes e documentação de modelos SQL |
| Engine analítica | DuckDB | OLAP in-process, zero infra, roda direto no Parquet |
| Orquestração | Python script | Substitui Airflow para execução local sem Docker |

---

## Modelos dbt

```
staging/
  stg_yellow_trips        → renomeação e padronização de colunas

intermediate/
  int_trips_enriched      → enriquecimento com dimensões de negócio

marts/
  fct_trips               → fact table (granularidade: 1 linha/corrida)
  mart_daily_summary      → agregação diária para análise de tendência
```

---

## Como rodar

### 1. Ambiente Python

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Pipeline completo

```bash
python pipeline/run_pipeline.py
```

Isso executa em sequência:
1. Download do dataset NYC TLC (raw)
2. Limpeza e validação (trusted)
3. `dbt run` — materializa os modelos
4. `dbt test` — executa os testes de qualidade

### 3. Rodar etapas individualmente

```bash
# Somente ingestão
python ingestion/ingest_raw.py

# Somente transformação trusted
python pipeline/transform_trusted.py

# Somente dbt
cd dbt_project
dbt run
dbt test
dbt docs generate && dbt docs serve
```

### 4. Consultar os dados com DuckDB

```python
import duckdb

con = duckdb.connect("data/refined/nyc_taxi.duckdb")

# Receita diária de Janeiro
con.execute("""
    SELECT pickup_date, total_trips, total_revenue, avg_tip_percentage
    FROM marts.mart_daily_summary
    ORDER BY pickup_date
""").df()
```

---

## Testes de qualidade

Os testes dbt cobrem:

- **not_null** em todas as colunas críticas
- **unique** em surrogate keys
- **accepted_values** em colunas categóricas (payment_type, time_of_day, distance_bucket)
- **relationships** entre staging e marts

```bash
cd dbt_project && dbt test
```

---

## Próximos passos

- [ ] Adicionar orquestração com Airflow (requer Docker)
- [ ] Expandir para múltiplos meses e particionar por data
- [ ] Adicionar camada de qualidade com Great Expectations
- [ ] Implementar SCD Type 2 para dimensão de zonas NYC
- [ ] Expor mart via API REST com FastAPI

---

## Estrutura do projeto

```
nyc_taxi_lakehouse/
├── data/
│   ├── raw/              # dado bruto, imutável
│   ├── trusted/          # dado limpo, sem regra de negócio
│   └── refined/          # DuckDB com modelos materializados
├── ingestion/
│   └── ingest_raw.py
├── pipeline/
│   ├── transform_trusted.py
│   └── run_pipeline.py
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── dbt_project.yml
│   └── profiles.yml
├── requirements.txt
└── README.md
```
