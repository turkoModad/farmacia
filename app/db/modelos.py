import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    BigInteger,
    Numeric,
    Boolean
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class Producto(Base):
    """
    Maestro de Productos
    """
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(BigInteger, unique=True, index=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    droga = Column(String(500), nullable=True)
    rubro = Column(String(100), nullable=True)
    funcion = Column(String(100), nullable=True)
    presentacion = Column(String(100), nullable=True)
    laboratorio = Column(String(100), nullable=True)
    activo = Column(Boolean, nullable=False, default=True)

    compras = relationship(
        "Compras",
        back_populates="producto_rel"
    )

    def __repr__(self):
        return (
            f"<Producto("
            f"codigo={self.codigo}, "
            f"nombre={self.nombre}, "
            f"activo={self.activo})>"
        )


class Compras(Base):
    """
    Líneas de compras realizadas por la farmacia.
    """
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, autoincrement=True)
    factura = Column(String(50), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False)
    codigo = Column( BigInteger, index=True, nullable=False)
    fecha = Column( DateTime(timezone=False), nullable=False)
    cant_ped = Column( Integer, default=0)
    cant_fact = Column( Integer, default=0)
    cant_entr = Column( Integer, default=0)
    precio_unitario = Column( Numeric(12, 2), nullable=False)
    precio_total = Column( Numeric(12, 2), nullable=False)
    diferencia_pedido_entrega = Column( Integer, default=0)
    estado_pedido = Column( String(20), default="Incompleto")

    producto_rel = relationship( "Producto", back_populates="compras")

    def __repr__(self):
        return (
            f"<Compras("
            f"factura={self.factura}, "
            f"producto={self.producto_rel.nombre if self.producto_rel else 'N/A'})>"
        )


class ProductoComprado(Base):
    """
    Subconjunto del maestro que contiene únicamente
    los productos que han tenido compras.
    """
    __tablename__ = "productos_comprados"

    id = Column( Integer, ForeignKey( "productos.id", ondelete="CASCADE" ), primary_key=True )

    maestro_rel = relationship(
        "Producto",
        backref="comprado_rel"
    )

    def __repr__(self):
        return f"<ProductoComprado(id={self.id})>"