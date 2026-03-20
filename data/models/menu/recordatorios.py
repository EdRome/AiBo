from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RecordatorioItemModelo(BaseModel):
    titulo: Optional[str] = Field(default=None)
    descripcion: Optional[str] = Field(default=None)
    fecha_recordatorio: Optional[datetime] = Field(default=None)

class RecordatorioItem(BaseModel):
    id: Optional[int] = Field(default=0)
    titulo: Optional[str] = Field(default=None)
    descripcion: Optional[str] = Field(default=None)
    estatus: Optional[str] = Field(default="activo")
    fecha_recordatorio: Optional[datetime] = Field(default=None)
    fecha_creacion: Optional[datetime] = Field(default=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=datetime.utcnow)
    keywords: Optional[List[str]] = Field(default=[])
    task_id: Optional[str] = Field(default=None)

class Recordatorio(BaseModel):
    # Campos de estado de la máquina
    active: bool = Field(default=False)
    step: str = Field(default="waiting_reminder")
    
    # Historial de mensajes (para compatibilidad con executor genérico)
    aibo_message: List[str] = Field(strict=True, default=[], validate_default=True)
    user_message: List[str] = Field(strict=True, default=[], validate_default=True)
    llm_response: str = Field(strict=True, default="", validate_default=True)

    # Campos del recordatorio
    recordatorio: Optional[RecordatorioItem] = Field(default=RecordatorioItem())