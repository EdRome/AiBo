import os
from datetime import datetime
from sqlalchemy import MetaData, Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase

schema = os.environ.get("DB_SCHEMA")
metadata_obj = MetaData(schema=schema)

class Base(DeclarativeBase):
    metadata = metadata_obj

class MensajesDescrube(Base):
    __tablename__ = "mensajes_descrube"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    mensaje = Column(String)
    funcionalidad = Column(String)
