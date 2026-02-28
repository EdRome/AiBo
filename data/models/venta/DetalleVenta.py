from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class DetalleVentaBase(BaseModel):
    producto: str = Field(default="")
    cantidad: int = Field(default=1)
    precio_unitario: float = Field(default=0.0)

class DetalleVentaCreate(DetalleVentaBase):
    pass

class DetalleVenta(DetalleVentaBase):
    # venta_id : int
    model_config = ConfigDict(from_attributes=True)