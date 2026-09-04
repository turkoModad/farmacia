from fastapi import APIRouter, Query, HTTPException, Depends
import logging
from app.services.consultas import (
    obtener_datos_anuales,
    obtener_compras_mensuales,
    obtener_compras_diarias,
    obtener_top_productos,
    obtener_lista_productos,
    obtener_precios_producto
)
from app.auth.dependencies import get_current_active_user
from app.auth.models import User


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/dashboard/anual")
def anual(
    fecha_inicio: str = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: str = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene datos agregados por año - Requiere autenticación"""
    try:
        logger.info(f"Usuario {current_user.username} consultó datos anuales")
        return obtener_datos_anuales(fecha_inicio, fecha_fin)
    except Exception as e:
        logger.error(f"Error en anual: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/api/dashboard/compras")
async def ventas(
    fecha_inicio: str = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: str = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene compras agregadas por mes - Requiere autenticación"""
    try:
        logger.info(f"Usuario {current_user.username} consultó compras mensuales")
        return obtener_compras_mensuales(fecha_inicio, fecha_fin)
    except Exception as e:
        logger.error(f"Error en compras: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/api/dashboard/compras-diarias")
async def compras_diarias(
    fecha_inicio: str = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: str = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene compras agregadas por día - Requiere autenticación"""
    try:
        logger.info(f"Usuario {current_user.username} consultó compras diarias")
        return obtener_compras_diarias(fecha_inicio, fecha_fin)
    except Exception as e:
        logger.error(f"Error en compras_diarias: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/api/dashboard/compras-productos")
async def compras_productos(
    fecha_inicio: str = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: str = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    limite: int = Query(40, description="Cantidad de productos a retornar"),
    offset: int = Query(0, description="Número de productos a saltar"),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene el top de productos más vendidos - Requiere autenticación"""
    try:
        logger.info(f"Usuario {current_user.username} consultó top productos")
        return obtener_top_productos(fecha_inicio, fecha_fin, limite, offset)
    except Exception as e:
        logger.error(f"Error en compras_productos: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/api/dashboard/productos-lista")
async def get_lista_productos(
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene lista de todos los productos únicos - Requiere autenticación"""
    try:
        logger.info(f"Usuario {current_user.username} consultó lista de productos")
        return obtener_lista_productos()
    except Exception as e:
        logger.error(f"Error en get_lista_productos: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/api/dashboard/precios-producto")
async def get_precios_producto(
    producto: str = Query(..., description="Nombre del producto"),
    fecha_inicio: str = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: str = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna evolución de precios unitarios con filtro de variación > 10.
    Requiere autenticación.
    """
    try:
        logger.info(f"Usuario {current_user.username} consultó precios de {producto}")
        return obtener_precios_producto(producto, fecha_inicio, fecha_fin)
    except Exception as e:
        logger.error(f"Error en get_precios_producto: {e}")
        raise HTTPException(status_code=500, detail=str(e))