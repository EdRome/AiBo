import os
from typing import List
from sqlalchemy import MetaData, Column, Integer, String, Float, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

schema = os.environ.get("DB_SCHEMA")
metadata_obj = MetaData(schema=schema)

class Base(DeclarativeBase):
    metadata = metadata_obj

class Memory(Base):
    __tablename__ = "memory"
    user_id = Column(String)
    active_context = Column(String)
    machine_stack = Column(List[String])
    global_memory = Column(JSONB)
    local_state = Column(JSONB)
    last_interaction = Column(DateTime)
    task_name = Column(String)
    creditos_disponibles = Column(Integer)