import os
from sqlalchemy import MetaData, Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from zoneinfo import ZoneInfo

tz_cdmx = ZoneInfo("America/Mexico_City")

schema = os.environ.get("DB_SCHEMA")
metadata_obj = MetaData(schema=schema)

class Base(DeclarativeBase):
    metadata = metadata_obj

class Message(Base):
    __tablename__ = "whatsapp"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now(tz_cdmx))
    sender = Column(String)
    receiver = Column(String)
    body = Column(String)
    data = Column(JSONB)
    multimedia = Column(String)