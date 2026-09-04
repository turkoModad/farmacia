import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Pipeline")

BASE_DIR = Path(__file__).resolve().parents[2]


def run_script():

    logger.info("Ejecutando: actualizar_db.py")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.actualizacion.actualizar_db"
        ],
        cwd=BASE_DIR
    )

    if result.returncode != 0:
        logger.error("Error en actualizar_db.py")
        raise RuntimeError(
            "Pipeline detenido por error en actualizar_db.py"
        )

    logger.info("OK: actualizar_db.py finalizado")


def main():

    logger.info("INICIANDO PIPELINE")

    run_script()

    logger.info("PIPELINE FINALIZADO CORRECTAMENTE")


if __name__ == "__main__":
    main()