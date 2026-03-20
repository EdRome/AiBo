import os
from sqlalchemy import MetaData, Column, Integer, String, Float, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime

schema = os.environ.get("DB_SCHEMA")
metadata_obj = MetaData(schema=schema)

class EstatusRecordatorio(Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    EJECUTADO = "ejecutado"
    BORRADO = "borrado"

class Base(DeclarativeBase):
    metadata = metadata_obj

class Recordatorio(Base):
    __tablename__ = "recordatorios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)
    titulo = Column(String)
    descripcion = Column(String)
    estatus = Column(EstatusRecordatorio)
    fecha_recordatorio = Column(DateTime)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow)
    keywords = Column(ARRAY(String))
    