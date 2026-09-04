import pandas as pd
from sqlalchemy import create_engine, text

from pathlib import Path
from app.variables import DATABASE_URL

ROOT = Path(__file__).resolve().parents[2]

ARCHIVO = ROOT / "archivos" / "compras.txt"

engine = create_engine(DATABASE_URL)


registros = []

with open(ARCHIVO, encoding="utf-8", errors="replace") as f:

    next(f)

    for linea in f:

        linea = linea.strip()

        if not linea:
            continue

        partes = [p.strip() for p in linea.split(",")]

        factura = partes[0]
        codigo = partes[-7]
        medio = partes[-6]
        fecha = partes[-5]
        cant_ped = partes[-4]
        cant_fact = partes[-3]
        cant_entr = partes[-2]
        precio = partes[-1]

        producto = ",".join(partes[1:-7]).strip()
        producto = producto.replace(",", ".")

        precio = precio.replace("$", "").strip()

        registros.append([
            factura,
            producto,
            codigo,
            medio,
            fecha,
            cant_ped,
            cant_fact,
            cant_entr,
            precio
        ])


df = pd.DataFrame(
    registros,
    columns=[
        "factura",
        "producto",
        "codigo",
        "medio",
        "fecha",
        "cant_ped",
        "cant_fact",
        "cant_entr",
        "precio_total"
    ]
)


df["codigo"] = pd.to_numeric(
    df["codigo"],
    errors="coerce"
).astype("int64")

df["cant_ped"] = pd.to_numeric(
    df["cant_ped"],
    errors="coerce"
).astype("int64")

df["cant_fact"] = pd.to_numeric(
    df["cant_fact"],
    errors="coerce"
).astype("int64")

df["cant_entr"] = pd.to_numeric(
    df["cant_entr"],
    errors="coerce"
).astype("int64")

df["precio_total"] = pd.to_numeric(
    df["precio_total"],
    errors="coerce"
).round(2)

df["fecha"] = pd.to_datetime(
    df["fecha"],
    errors="coerce"
)


df = df[df["cant_entr"] > 0].copy()


with engine.connect() as conn:

    df_productos = pd.read_sql(
        text("""
            SELECT
                id,
                codigo
            FROM productos
        """),
        conn
    )


codigos_maestro = set(
    df_productos["codigo"].astype("int64")
)

codigos_compras = set(
    df["codigo"].astype("int64")
)

codigos_nuevos = codigos_compras - codigos_maestro


if codigos_nuevos:

    productos_nuevos = (
        df[df["codigo"].isin(codigos_nuevos)]
        [["codigo", "producto"]]
        .drop_duplicates(subset=["codigo"])
    )

    with engine.begin() as conn:

        for _, fila in productos_nuevos.iterrows():

            codigo = int(fila["codigo"])
            nombre = str(fila["producto"]).strip()

            conn.execute(
                text("""
                    INSERT INTO productos (
                        codigo,
                        nombre,
                        activo
                    )
                    VALUES (
                        :codigo,
                        :nombre,
                        TRUE
                    )
                    ON CONFLICT (codigo) DO NOTHING
                """),
                {
                    "codigo": codigo,
                    "nombre": nombre
                }
            )

        nuevos_ids = conn.execute(
            text("""
                SELECT
                    id,
                    codigo
                FROM productos
                WHERE codigo = ANY(:codigos)
            """),
            {
                "codigos": list(codigos_nuevos)
            }
        ).fetchall()

        for fila in nuevos_ids:

            conn.execute(
                text("""
                    INSERT INTO productos_comprados (id)
                    VALUES (:id)
                    ON CONFLICT (id) DO NOTHING
                """),
                {
                    "id": fila.id
                }
            )


with engine.connect() as conn:

    df_productos = pd.read_sql(
        text("""
            SELECT
                id,
                codigo
            FROM productos
        """),
        conn
    )


df = df.merge(
    df_productos,
    on="codigo",
    how="left"
)

df = df.rename(columns={
    "id": "producto_id"
})


df["precio_unitario"] = (
    df["precio_total"] / df["cant_entr"]
).round(2)

df["diferencia_pedido_entrega"] = (
    df["cant_ped"] - df["cant_entr"]
)

df["estado_pedido"] = (
    df["cant_ped"] == df["cant_entr"]
).map({
    True: "Completo",
    False: "Incompleto"
})


df_compras_final = df[
    [
        "factura",
        "producto_id",
        "codigo",
        "fecha",
        "cant_ped",
        "cant_fact",
        "cant_entr",
        "precio_unitario",
        "precio_total",
        "diferencia_pedido_entrega",
        "estado_pedido"
    ]
].copy()


columnas_compras = [
    "factura",
    "producto_id",
    "codigo",
    "fecha",
    "cant_ped",
    "cant_fact",
    "cant_entr",
    "precio_unitario",
    "precio_total",
    "diferencia_pedido_entrega",
    "estado_pedido"
]


if df_compras_final.columns.tolist() != columnas_compras:
    raise ValueError(
        "Las columnas de df_compras_final no coinciden "
        "con las columnas esperadas."
    )


if df_compras_final["producto_id"].isna().any():
    raise ValueError(
        "Existen compras sin producto_id."
    )


if (df_compras_final["cant_entr"] <= 0).any():
    raise ValueError(
        "Existen registros con cant_entr <= 0."
    )


if df_compras_final["precio_unitario"].isin(
    [float("inf"), float("-inf")]
).any():
    raise ValueError(
        "Existen precios unitarios infinitos."
    )


if df_compras_final.isna().any().any():
    raise ValueError(
        "Existen valores nulos en df_compras_final."
    )


with engine.connect() as conn:

    df_existentes = pd.read_sql(
        text("""
            SELECT
                factura,
                producto_id,
                codigo,
                fecha,
                cant_ped,
                cant_fact,
                cant_entr,
                precio_unitario,
                precio_total,
                diferencia_pedido_entrega,
                estado_pedido
            FROM compras
        """),
        conn
    )


for columna in ["precio_unitario", "precio_total"]:

    df_existentes[columna] = pd.to_numeric(
        df_existentes[columna]
    ).round(2)

    df_compras_final[columna] = pd.to_numeric(
        df_compras_final[columna]
    ).round(2)


df_existentes["fecha"] = pd.to_datetime(
    df_existentes["fecha"]
)

df_compras_final["fecha"] = pd.to_datetime(
    df_compras_final["fecha"]
)


duplicados_txt = df_compras_final.duplicated(
    subset=columnas_compras,
    keep=False
)

if duplicados_txt.any():

    raise ValueError(
        f"El TXT contiene {duplicados_txt.sum()} "
        "registros duplicados."
    )


df_nuevas = df_compras_final.merge(
    df_existentes.drop_duplicates(
        subset=columnas_compras
    ),
    on=columnas_compras,
    how="left",
    indicator=True
)

df_nuevas = df_nuevas[
    df_nuevas["_merge"] == "left_only"
].drop(columns="_merge")


if df_nuevas.empty:

    print("No hay compras nuevas para insertar.")

else:

    registros = df_nuevas.to_dict(
        orient="records"
    )

    query_insert = text("""
        INSERT INTO compras (
            factura,
            producto_id,
            codigo,
            fecha,
            cant_ped,
            cant_fact,
            cant_entr,
            precio_unitario,
            precio_total,
            diferencia_pedido_entrega,
            estado_pedido
        )
        VALUES (
            :factura,
            :producto_id,
            :codigo,
            :fecha,
            :cant_ped,
            :cant_fact,
            :cant_entr,
            :precio_unitario,
            :precio_total,
            :diferencia_pedido_entrega,
            :estado_pedido
        )
    """)

    with engine.begin() as conn:

        conn.execute(
            query_insert,
            registros
        )

    print(
        f"Se insertaron {len(registros)} compras nuevas."
    )