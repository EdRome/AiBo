from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class DetalleGastoBase(BaseModel):
    producto: str = Field(default="")
    cantidad: int = Field(default=1)
    precio_unitario: float = Field(default=0.0)

class DetalleGastoCreate(DetalleGastoBase):
    pass

class DetalleGasto(DetalleGastoBase):
    model_config = ConfigDict(from_attributes=True)