import os
from sqlalchemy import MetaData, Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from zoneinfo import ZoneInfo

schema = os.environ.get("DB_SCHEMA")
metadata_obj = MetaData(schema=schema)

tz_cdmx = ZoneInfo("America/Mexico_City")

class Base(DeclarativeBase):
    metadata = metadata_obj

class UserCredentials(Base):
    __tablename__ = "user_credentials"
    user_id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.now(tz_cdmx))
    google_token_data = Column(JSONB)
    updated_at = Column(DateTime, default=datetime.now(tz_cdmx))