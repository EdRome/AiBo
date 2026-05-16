from decimal import Decimal
from sqlalchemy import MetaData, Column, Integer, String, Float, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid

# Definimos los metadatos con el esquema por defecto para todos los modelos
metadata_obj = MetaData(schema="transactional")

class Base(DeclarativeBase):
    metadata = metadata_obj

class ProductosDB(Base):
    __tablename__ = "productos"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, nullable=False)
    marca = Column(String, nullable=False)
    nombre_base = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

class ProductosAliasDB(Base):
    __tablename__ = "productos_alias"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    producto_id = Column(String, ForeignKey("productos.id"))
    nombre_alias = Column(String, nullable=False)

class ProductosSKUDB(Base):
    __tablename__ = "productos_sku"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    producto_id = Column(String, ForeignKey("productos.id"))
    precio_venta = Column(Numeric(precision=10, scale=2), nullable=False)
    sku = Column(String, nullable=False)
    costo = Column(Numeric(precision=10, scale=2), nullable=False)
    atributos = Column(JSONB, nullable=False)
    stock_actual = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class TrazabilidadDB(Base):
    __tablename__ = "trazabilidad"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    sku_id = Column(String, ForeignKey("productos_sku.id"))
    tipo = Column(Enum('ENTRADA','SALIDA','VENTA','MERMA','AJUSTE'), nullable=False)
    cantidad = Column(Integer, nullable=False) 
    phone_number = Column(String, nullable=False)
    whatsapp_msg_id = Column(Integer, ForeignKey("whatsapp.id"))
    created_at = Column(DateTime, default=datetime.now)
