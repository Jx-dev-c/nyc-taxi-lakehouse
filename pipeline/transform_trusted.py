"""
pipeline/transform_trusted.py
------------------------------
Camada trusted: aplica limpeza, validações e tipagem correta sobre a raw.
Nenhuma regra de negócio aqui — apenas garantia de qualidade do dado.

Decisão arquitetural:
    Separar trusted de refined permite reprocessar regras de negócio
    sem reingesting dados. A trusted é o contrato de qualidade mínima
    que todas as camadas downstream podem confiar.
"""

import logging
import sys
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "yellow_tripdata_2023-01.parquet"
TRUSTED_PATH = Path(__file__).resolve().parents[1] / "data" / "trusted" / "yellow_tripdata_2023-01.parquet"


def apply_quality_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica filtros de qualidade sem regra de negócio.
    Remove registros tecnicamente inválidos — não registros que o negócio
    considera outliers. Essa distinção é intencional.
    """
    original_count = len(df)

    # Remove trips com coordenadas nulas (dado tecnicamente corrompido)
    df = df.dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime"])

    # Remove trips com duração negativa ou zero (impossível fisicamente)
    df = df[df["tpep_dropoff_datetime"] > df["tpep_pickup_datetime"]]

    # Remove trips com distância negativa
    df = df[df["trip_distance"] >= 0]

    # Remove trips com valor total negativo (estorno já tratado separadamente)
    df = df[df["total_amount"] >= 0]

    # Remove trips com passenger_count inválido
    df = df[df["passenger_count"].between(1, 9, inclusive="both")]

    removed = original_count - len(df)
    logger.info(
        "Qualidade: %d registros removidos (%.2f%% do total)",
        removed,
        (removed / original_count) * 100,
    )

    return df


def cast_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garante tipagem correta das colunas.
    Parquet preserva tipos, mas conversões explícitas evitam surpresas
    com versões diferentes de pandas/pyarrow.
    """
    df = df.copy()

    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    df["passenger_count"] = df["passenger_count"].astype("Int64")
    df["RatecodeID"] = df["RatecodeID"].astype("Int64")
    df["payment_type"] = df["payment_type"].astype("Int64")

    return df


def enrich_with_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona colunas derivadas puramente técnicas (sem regra de negócio).
    Ex: duração da corrida em minutos — é matemática, não interpretação.
    """
    df = df.copy()

    df["trip_duration_minutes"] = (
        (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"])
        .dt.total_seconds()
        / 60
    ).round(2)

    df["pickup_date"] = df["tpep_pickup_datetime"].dt.date
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour

    return df


def transform_trusted(raw_path: Path, trusted_path: Path) -> None:
    logger.info("Lendo camada raw: %s", raw_path)
    df_raw = pd.read_parquet(raw_path)
    logger.info("Raw carregado: %d linhas", len(df_raw))

    df_trusted = (
        df_raw
        .pipe(cast_schema)
        .pipe(apply_quality_filters)
        .pipe(enrich_with_derived_columns)
    )

    trusted_path.parent.mkdir(parents=True, exist_ok=True)
    df_trusted.to_parquet(trusted_path, index=False)

    logger.info(
        "Trusted gerado: %d linhas | %.2f MB | path: %s",
        len(df_trusted),
        trusted_path.stat().st_size / (1024 ** 2),
        trusted_path,
    )


def main() -> None:
    transform_trusted(RAW_PATH, TRUSTED_PATH)


if __name__ == "__main__":
    main()
