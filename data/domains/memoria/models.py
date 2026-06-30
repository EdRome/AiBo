import os
from sqlalchemy import MetaData, Column, Integer, String, DateTime, 
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime

schema = os.environ.get("DB_SCHEMA")
metadata_obj = MetaData(schema=schema)

class Base(DeclarativeBase):
    metadata = metadata_obj

class Memory(Base):
    __tablename__ = "memory"
    user_id = Column(String, primary_key=True)
    active_context = Column(String)
    machine_stack = Column(ARRAY(String))
    global_memory = Column(JSONB)
    local_state = Column(JSONB)
    last_interaction = Column(DateTime)
    task_name = Column(String, default="")
    creditos_disponibles = Column(Integer)

class MemoriaEstados(Base):
    __tablename__ = "memoria_estados"
    user_id = Column(String, primary_key=True)
    estado_actual = Column(String)
    progreso_nivel = Column(Integer)
    nivel_actual = Column(String)
    contexto_json = Column(JSONB)
    siguiente_nivel = Column(String)
    misiones = Column(ARRAY(String))