import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn
import sys
import asyncio
from pathlib import Path
import subprocess
import os

from app.db.database import engine, Base, get_db
import app.db.modelos  
from app.routers.compras import router as compras_router
from app.routers.auth import router as auth_router
from app.auth.dependencies import get_current_active_user


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MainAPI")


PIPELINE = Path(__file__).resolve().parent / "app" / "actualizacion" / "pipeline.py"


def run_pipeline():
    """
    Ejecuta ETL completo (actualizar + importar).
    Corre en proceso separado.
    """
    try:
        subprocess.run([sys.executable, str(PIPELINE)], check=True)
        logger.info("Pipeline ejecutado correctamente.")
    except Exception as e:
        logger.error(f"Error ejecutando pipeline: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Iniciando servidor FastAPI...")

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Base de datos lista.")

        if os.environ.get("RUN_MAIN", "true") == "true":
            asyncio.create_task(asyncio.to_thread(run_pipeline))

    except Exception as e:
        logger.critical(f"Error en startup: {e}")
        raise

    yield

    logger.info("Cerrando servidor...")
    await engine.dispose()
    logger.info("Conexiones cerradas correctamente.")


app = FastAPI(
    title="API de Control de Farmacia",
    version="1.0.0",
    lifespan=lifespan
)

STATIC_DIR = Path(__file__).resolve().parent / "frontend" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


app.include_router(auth_router)
app.include_router(compras_router)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Sirve la página de login o dashboard según autenticación"""
    try:
        # Siempre servir login.html como página principal
        login_path = Path(__file__).resolve().parent / "frontend" / "templates" / "login.html"
        return FileResponse(str(login_path))
    except Exception as e:
        logger.error(f"Error al servir login.html: {e}")
        return HTMLResponse(content=f"<h1>Error al cargar la página</h1><p>{str(e)}</p>", status_code=500)



@app.get("/dashboard")
async def dashboard():
    """Sirve el dashboard (solo accesible con autenticación)"""
    try:
        index_path = Path(__file__).resolve().parent / "frontend" / "templates" / "index.html"
        return FileResponse(str(index_path))
    except Exception as e:
        logger.error(f"Error al servir dashboard: {e}")
        return HTMLResponse(content=f"<h1>Error al cargar el dashboard</h1><p>{str(e)}</p>", status_code=500)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8550,
        reload=True
    )