import os
from pathlib import Path
from dotenv import load_dotenv
import logging


logger = logging.getLogger("Config")

base_dir = Path(__file__).resolve().parent
ruta_env = base_dir.parent / ".env"

if not load_dotenv(dotenv_path=ruta_env, override=True):
    logger.warning(f"No se pudo cargar el archivo .env desde la ruta: {ruta_env}")


try:
    DB_USER = os.getenv("DB_USER", "").strip()
    DB_PASSWORD = os.getenv("DB_PASSWORD", "").strip()
    DB_HOST = os.getenv("DB_HOST", "").strip()
    DB_PORT = os.getenv("DB_PORT", "").strip()
    DB_NAME = os.getenv("DB_NAME", "").strip()
    SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
    ALGORITHM = os.getenv("ALGORITHM", "").strip()

    if not DB_HOST or DB_HOST == "localhost" or "DB_HOST" in DB_HOST:
        DB_HOST = "127.0.0.1"

    variables = [DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]
    if any(v == "" for v in variables):
        raise ValueError(
            f"Una o más variables obligatorias faltan o están vacías en el archivo .env. Ruta buscada: {ruta_env}"
        )

except Exception as e:
    logger.critical(f"No se pudieron cargar los recursos base. Motivo: {e}")
    raise e


USER_DATABASE_URL=f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

DATABASE_URL=f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'