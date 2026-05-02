from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List
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