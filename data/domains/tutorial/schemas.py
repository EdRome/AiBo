from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class Onboarding(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre del usuario")
    nombre_negocio: Optional[str] = Field(None, description="Nombre del negocio del usuario")