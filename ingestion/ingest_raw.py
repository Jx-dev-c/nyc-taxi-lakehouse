"""
ingestion/ingest_raw.py
-----------------------
Responsável por baixar os dados públicos do NYC TLC Taxi Trips
e persistir na camada raw como Parquet, sem nenhuma transformação.

Decisão arquitetural:
    A camada raw é imutável por convenção. Nenhuma lógica de negócio
    é aplicada aqui — apenas conversão de formato (CSV -> Parquet)
    para eficiência de leitura nas camadas downstream.
"""

import logging
import sys
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Dataset público NYC TLC - Janeiro 2023 (Yellow Taxi)
# Fonte: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
RAW_DATA_URL = (
    "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"
)

RAW_OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "yellow_tripdata_2023-01.parquet"


def download_raw_data(url: str, output_path: Path) -> None:
    """
    Faz o download do dataset e persiste em Parquet na camada raw.
    Nenhuma transformação é aplicada — dado bruto preservado integralmente.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        logger.info("Arquivo já existe em raw. Pulando download: %s", output_path)
        return

    logger.info("Iniciando download: %s", url)

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    # O arquivo já vem em Parquet direto da fonte TLC
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info("Download concluído. Arquivo salvo em: %s", output_path)

    # Validação mínima: garante que o arquivo é um Parquet legível
    df_sample = pd.read_parquet(output_path)
    logger.info(
        "Validação raw: %d linhas | %d colunas | %.2f MB",
        len(df_sample),
        len(df_sample.columns),
        output_path.stat().st_size / (1024 ** 2),
    )


def main() -> None:
    download_raw_data(RAW_DATA_URL, RAW_OUTPUT_PATH)


if __name__ == "__main__":
    main()
