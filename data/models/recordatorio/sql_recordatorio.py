import os
from sqlalchemy import MetaData, Column, String, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from zoneinfo import ZoneInfo

schema = os.environ.get("DB_SCHEMA")
metadata_obj = MetaData(schema=schema)

tz_cdmx = ZoneInfo("America/Mexico_City")

class Base(DeclarativeBase):
    metadata = metadata_obj

class Recordatorio(Base):
    __tablename__ = "recordatorio"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now(tz_cdmx))
    phone_number = Column(String)
    task_id = Column(String)
    fecha_recordatorio = Column(DateTime)
    mensaje = Column(String)
    time_delta = Column(Integer)
    status = Column(String)