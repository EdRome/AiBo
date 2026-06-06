from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo

tz_cdmx = ZoneInfo("America/Mexico_City")

class RecordatorioBase(BaseModel):
    fecha_recordatorio: datetime = Field(default=datetime.now(tz_cdmx))
    recordatorio: str = Field(default="")

class Recordatorio(RecordatorioBase):
    phone_number: str
    created_at: datetime = Field(default=datetime.now(tz_cdmx))
    time_delta: int = Field(default=0)
    task_id: str = Field(default="")
    status: str = Field(default="pending")
    
    def calcula_delta(self):
        self.time_delta = self.created_at - self.fecha_recordatorio

class ListaRecordatorios(BaseModel):
    recordatorios: List[RecordatorioBase]

class RemainderQueryExtraction(BaseModel):
    rango_solicitado: str = Field(
        ..., 
        description='Rango de la solicitud, puede ser: "hoy" | "ayer" | "mañana" | "esta_semana" | "semana_pasada" | "semana_siguiente" | "este_mes" | "mes_pasado" | "mes_siguiente" | "dia_especifico_semana" | "especifico"'
    )
    dia_semana: Optional[int] = Field(
        ..., 
        description='Día de específico de la semana, puede ser: null | int(0-6). Lunes es 0, domingo es 6'
    )
    relacion_semana: Optional[str] = Field(
        ..., 
        description='Relación con la semana actual, puede ser: null | "actual" | "pasada" | "siguiente"'
    )
    mes_especifico: Optional[int] = Field(
        ...,
        description='Mes de análisis, puede ser: null | int (1-12)'
    )
    search_query: Optional[str] = Field(
        None, description="Palabra clave, nombre de persona o acción específica a buscar en la descripción"
    )