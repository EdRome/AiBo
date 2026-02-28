from pydantic import BaseModel, Field
from data.models.etapa2.needs import NeedsAnalysis

class Summary(BaseModel):
    summary: str = Field(strict=True, default="", validate_default=True)
    giro: str = Field(strict=True, default="", validate_default=True)
    descripcion: str = Field(strict=True, default="", validate_default=True)

class Emprendedor(BaseModel):
    nombre: str = Field(strict=True, default="", validate_default=True)
    nombre_negocio: str = Field(strict=True, default="", validate_default=True)

class DatosNegocio(BaseModel):
    emprendedor: Emprendedor = Field(strict=True, default=Emprendedor(), validate_default=True)
    negocio: Summary = Field(strict=True, default=Summary(), validate_default=True)
    producto_mas_vendido: str = Field(strict=True, default="", validate_default=True)
    needs: NeedsAnalysis = Field(strict=True, default=NeedsAnalysis(), validate_default=True)