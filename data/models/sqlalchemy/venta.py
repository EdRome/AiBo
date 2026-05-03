import os
from sqlalchemy import MetaData, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime

# Definimos los metadatos con el esquema por defecto para todos los modelos
schema = os.environ.get("DB_SCHEMA")
metadata_obj = MetaData(schema=schema)

class Base(DeclarativeBase):
    metadata = metadata_obj

class VentaDB(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metodo_pago = Column(String, default="efectivo")
    total = Column(Float, default=0.0)
    fecha = Column(DateTime, default=datetime.utcnow)
    
    # Relación: al borrar la venta, se borran sus detalles (cascade)
    detalles = relationship("DetalleVentaDB", back_populates="venta", cascade="all, delete-orphan")
    phone_number = Column(String)

class DetalleVentaDB(Base):
    __tablename__ = "detalles_venta"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venta_id = Column(Integer, ForeignKey(f"{schema}.ventas.id"))
    producto = Column(String)
    cantidad = Column(Integer)
    precio_unitario = Column(Float)

    venta = relationship("VentaDB", back_populates="detalles")

class SalesSummaryDB(Base):
    __tablename__ = "sales_summary"

    phone_number = Column(String, primary_key=True)
    venta_total = Column(Float)
    unidades_vendidas = Column(Integer)
    num_ventas = Column(Integer)