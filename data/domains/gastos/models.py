import os
from sqlalchemy import MetaData, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime

# Definimos los metadatos con el esquema por defecto para todos los modelos
schema = os.environ.get("DB_SCHEMA", "transactional")
metadata_obj = MetaData(schema=schema)

class Base(DeclarativeBase):
    metadata = metadata_obj

class GastoDB(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metodo_pago = Column(String, default="efectivo")
    total = Column(Float, default=0.0)
    fecha = Column(DateTime, default=datetime.utcnow)

    # Relación: al borrar el gasto, se borran sus detalles (cascade)
    detalles = relationship("DetalleGastoDB", back_populates="gasto", cascade="all, delete-orphan")
    phone_number = Column(String)

class DetalleGastoDB(Base):
    __tablename__ = "detalles_gasto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    gasto_id = Column(Integer, ForeignKey("gastos.id"))
    producto = Column(String)
    cantidad = Column(Integer)
    precio_unitario = Column(Float)

    gasto = relationship("GastoDB", back_populates="detalles")

class ExpenseSummaryDB(Base):
    __tablename__ = "expense_summary"

    phone_number = Column(String, primary_key=True)
    gasto_total = Column(Float)
    unidades_gastadas = Column(Integer)
    num_gastos = Column(Integer)