"""
pipeline/run_pipeline.py
------------------------
Orquestrador local do pipeline completo.
Substitui o Airflow para execução local sem Docker.

Decisão arquitetural:
    Em produção, cada step seria uma task em um DAG do Airflow.
    Aqui, a sequência é explícita e os steps são funções importadas
    diretamente — a lógica de negócio não muda, só o orquestrador.
    Isso facilita a migração para Airflow/Prefect/Dagster no futuro.

Ordem de execução:
    1. ingest_raw     → baixa dado bruto, persiste em Parquet
    2. transform_trusted → limpa, valida e tipifica
    3. dbt run        → modelos de staging, intermediate e marts
    4. dbt test       → testes de qualidade definidos no dbt
"""

import logging
import subprocess
import sys
import time
from pathlib import Path

# Adiciona o root do projeto ao path para imports relativos
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingestion.ingest_raw import main as ingest_raw
from pipeline.transform_trusted import main as transform_trusted

# Evita mojibake em logs com acentos no console do Windows (cp1252 por padrão)
sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

DBT_PROJECT_PATH = Path(__file__).resolve().parents[1] / "dbt_project"
DATA_REFINED_PATH = Path(__file__).resolve().parents[1] / "data" / "refined"


def run_step(name: str, func) -> float:
    """Executa um step do pipeline com logging de tempo e tratamento de erro."""
    logger.info("=" * 50)
    logger.info("INICIANDO STEP: %s", name)
    start = time.time()

    try:
        func()
        elapsed = time.time() - start
        logger.info("STEP CONCLUÍDO: %s | %.2fs", name, elapsed)
        return elapsed
    except Exception as e:
        logger.error("FALHA NO STEP: %s | Erro: %s", name, str(e))
        raise


def resolve_dbt_executable() -> Path:
    """Resolve o executável do dbt instalado no mesmo venv do Python em uso.

    subprocess.run(["dbt", ...]) depende do PATH do processo e falha (WinError 2)
    quando o pipeline roda com um interpretador Python diferente do venv onde o
    dbt foi instalado (ex: python.exe global em vez de .venv\\Scripts\\python.exe).
    """
    dbt_name = "dbt.exe" if sys.platform == "win32" else "dbt"
    dbt_path = Path(sys.executable).parent / dbt_name
    if not dbt_path.exists():
        raise FileNotFoundError(
            f"dbt não encontrado em {dbt_path}. "
            "Rode o pipeline com o Python do venv onde as dependências foram "
            "instaladas (.venv\\Scripts\\python.exe pipeline\\run_pipeline.py)."
        )
    return dbt_path


def run_dbt_command(subcommand: list[str]) -> None:
    """Executa um comando dbt via subprocess a partir do diretório do projeto."""
    result = subprocess.run(
        [str(resolve_dbt_executable()), *subcommand],
        cwd=DBT_PROJECT_PATH,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.warning(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"dbt falhou com código {result.returncode}")


def main() -> None:
    logger.info("PIPELINE INICIADO")
    pipeline_start = time.time()

    timings = {}

    # Step 1: Ingestão raw
    timings["ingest_raw"] = run_step("ingest_raw", ingest_raw)

    # Step 2: Transformação trusted
    timings["transform_trusted"] = run_step("transform_trusted", transform_trusted)

    # DuckDB não cria o diretório do arquivo .duckdb sozinho: se "data/refined"
    # não existir, o dbt falha com um UnicodeDecodeError enganoso (o adapter
    # tenta decodificar como UTF-8 a mensagem de erro do Windows, que vem em
    # português com acentos, em vez de reportar "caminho não encontrado").
    DATA_REFINED_PATH.mkdir(parents=True, exist_ok=True)

    # Step 3: dbt run
    timings["dbt_run"] = run_step(
        "dbt_run",
        lambda: run_dbt_command(["run"]),
    )

    # Step 4: dbt test
    timings["dbt_test"] = run_step(
        "dbt_test",
        lambda: run_dbt_command(["test"]),
    )

    total = time.time() - pipeline_start
    logger.info("=" * 50)
    logger.info("PIPELINE CONCLUÍDO | Total: %.2fs", total)
    for step, elapsed in timings.items():
        logger.info("  %-25s %.2fs", step, elapsed)


if __name__ == "__main__":
    main()
