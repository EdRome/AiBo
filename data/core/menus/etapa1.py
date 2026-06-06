import os
import requests
from pydantic import BaseModel, Field
from typing import Optional, List

class Etapa1(BaseModel):
    active: bool = Field(default=False)
    step: str = Field(default="onboarding")
    
    user_message: List[str] = Field(default_factory=list)
    aibo_message: List[str] = Field(default_factory=list)

    def get_full_user_message(self):
        return "\n".join(self.user_message)

class Summary(BaseModel):
    summary: str = Field(strict=True, default="", validate_default=True)
    giro: str = Field(strict=True, default="", validate_default=True)
    descripcion: str = Field(strict=True, default="", validate_default=True)
    ubicacion: str = Field(strict=True, default="", validate_default=True)

class Emprendedor(BaseModel):
    nombre: str = Field(strict=True, default="", validate_default=True)
    nombre_negocio: str = Field(strict=True, default="", validate_default=True)

class DatosNegocio(BaseModel):
    emprendedor: Emprendedor = Field(strict=True, default=Emprendedor(), validate_default=True)
    negocio: Summary = Field(strict=True, default=Summary(), validate_default=True)
    producto_mas_vendido: str = Field(strict=True, default="", validate_default=True)

class EntityExtractor(BaseModel):
    nombre: str = Field(strict=True, default="", validate_default=True)
    nombre_negocio: str = Field(strict=True, default="", validate_default=True)
    giro: str = Field(strict=True, default="tendedor", validate_default=True)
    ubicacion: str = Field(strict=True, default="", validate_default=True)