import pandas as pd
from sqlalchemy import text
from app.db.database import engine_sync
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def obtener_datos_anuales(
    fecha_inicio: str = None,
    fecha_fin: str = None
) -> List[Dict[str, Any]]:
    """
    Obtiene datos agregados por año de compras.
    """
    try:
        sql = """
        SELECT
            EXTRACT(YEAR FROM fecha) AS anio,
            SUM(precio_total) AS compras
        FROM compras
        WHERE 1=1
        """

        params = {}

        if fecha_inicio:
            sql += " AND fecha >= :fecha_inicio"
            params["fecha_inicio"] = fecha_inicio

        if fecha_fin:
            sql += " AND fecha <= :fecha_fin"
            params["fecha_fin"] = fecha_fin

        sql += """
        GROUP BY EXTRACT(YEAR FROM fecha)
        ORDER BY anio;
        """

        df = pd.read_sql(
            text(sql),
            engine_sync,
            params=params
        )

        return df.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Error en obtener_datos_anuales: {e}")
        raise


def obtener_compras_mensuales(
    fecha_inicio: str = None,
    fecha_fin: str = None
) -> List[Dict[str, Any]]:
    """
    Obtiene compras agregadas por mes.
    """
    try:
        sql = """
        SELECT
            TO_CHAR(fecha, 'Mon YYYY') AS periodo,
            SUM(precio_total) AS compras
        FROM compras
        WHERE 1=1
        """

        params = {}

        if fecha_inicio:
            sql += " AND fecha >= :fecha_inicio"
            params["fecha_inicio"] = fecha_inicio

        if fecha_fin:
            sql += " AND fecha <= :fecha_fin"
            params["fecha_fin"] = fecha_fin

        sql += """
        GROUP BY TO_CHAR(fecha, 'Mon YYYY')
        ORDER BY MIN(fecha) ASC;
        """

        df = pd.read_sql(
            text(sql),
            engine_sync,
            params=params
        )

        return df.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Error en obtener_compras_mensuales: {e}")
        raise


def obtener_compras_diarias(
    fecha_inicio: str = None,
    fecha_fin: str = None
) -> List[Dict[str, Any]]:
    """
    Obtiene compras agregadas por día.
    """
    try:
        sql = """
        SELECT
            fecha::date AS dia,
            SUM(precio_total) AS compras
        FROM compras
        WHERE 1=1
        """

        params = {}

        if fecha_inicio:
            sql += " AND fecha >= :fecha_inicio"
            params["fecha_inicio"] = fecha_inicio

        if fecha_fin:
            sql += " AND fecha <= :fecha_fin"
            params["fecha_fin"] = fecha_fin

        sql += """
        GROUP BY fecha::date
        ORDER BY dia ASC;
        """

        df = pd.read_sql(
            text(sql),
            engine_sync,
            params=params
        )

        df["dia"] = df["dia"].astype(str)

        return df.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Error en obtener_compras_diarias: {e}")
        raise


def obtener_top_productos(
    fecha_inicio: str = None,
    fecha_fin: str = None,
    limite: int = 40,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Obtiene los productos más vendidos según cantidad entregada.
    """
    try:
        sql = """
        SELECT
            p.id AS producto_id,
            p.codigo,
            p.nombre AS producto,
            SUM(c.cant_entr) AS total_vendido,
            SUM(c.precio_total) AS total_recaudado
        FROM compras c
        JOIN productos p
            ON p.id = c.producto_id
        WHERE 1=1
        """

        params = {}

        if fecha_inicio:
            sql += " AND c.fecha >= :fecha_inicio"
            params["fecha_inicio"] = fecha_inicio

        if fecha_fin:
            sql += """
                AND c.fecha < CAST(:fecha_fin AS DATE) + INTERVAL '1 day'
            """
            params["fecha_fin"] = fecha_fin

        sql += """
        GROUP BY
            p.id,
            p.codigo,
            p.nombre
        ORDER BY total_vendido DESC
        LIMIT :limite
        OFFSET :offset;
        """

        params["limite"] = limite
        params["offset"] = offset

        df = pd.read_sql(
            text(sql),
            engine_sync,
            params=params
        )

        return df.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Error en obtener_top_productos: {e}")
        raise


def obtener_lista_productos() -> List[str]:
    """
    Obtiene únicamente los productos que tienen compras registradas.
    """
    try:
        sql = """
        SELECT DISTINCT
            p.nombre
        FROM compras c
        JOIN productos p
            ON p.id = c.producto_id
        ORDER BY p.nombre;
        """

        df = pd.read_sql(
            text(sql),
            engine_sync
        )

        return df["nombre"].tolist()

    except Exception as e:
        logger.error(f"Error en obtener_lista_productos: {e}")
        raise


def obtener_precios_producto(
    producto: str,
    fecha_inicio: str = None,
    fecha_fin: str = None
) -> List[Dict[str, Any]]:
    """
    Obtiene la evolución de precios unitarios de un producto
    que efectivamente tiene compras registradas.
    """
    try:
        sql = """
        SELECT
            c.fecha,
            c.precio_unitario
        FROM compras c
        JOIN productos p
            ON p.id = c.producto_id
        WHERE p.nombre = :producto
          AND c.precio_unitario IS NOT NULL
        """

        params = {
            "producto": producto
        }

        if fecha_inicio:
            sql += " AND c.fecha >= :fecha_inicio"
            params["fecha_inicio"] = fecha_inicio

        if fecha_fin:
            sql += """
                AND c.fecha < CAST(:fecha_fin AS DATE) + INTERVAL '1 day'
            """
            params["fecha_fin"] = fecha_fin

        sql += """
        ORDER BY c.fecha DESC;
        """

        df = pd.read_sql(
            text(sql),
            engine_sync,
            params=params
        )

        if df.empty:
            return []

        precios_filtrados = []
        ultimo_precio_mostrado = None

        for _, row in df.iterrows():

            precio = row["precio_unitario"]

            if precio is None:
                continue

            precio = float(precio)

            if (
                ultimo_precio_mostrado is None
                or abs(precio - ultimo_precio_mostrado) > 10
            ):
                precios_filtrados.append({
                    "fecha": row["fecha"].strftime("%Y-%m-%d"),
                    "precio": round(precio, 2)
                })

                ultimo_precio_mostrado = precio

        return precios_filtrados

    except Exception as e:
        logger.error(f"Error en obtener_precios_producto: {e}")
        raise