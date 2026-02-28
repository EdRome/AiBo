from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List
from data.models.venta.DetalleVenta import DetalleVenta, DetalleVentaCreate

class VentaBase(BaseModel):
    metodo_pago: str = Field(default="efectivo")
    total: float = Field(default=0.0)

class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate]

class Venta(VentaBase):
    phone_number: str
    fecha: datetime = Field(default=datetime.now())
    created_at: datetime = Field(default=datetime.now())
    detalles: List[DetalleVenta]

    model_config = ConfigDict(from_attributes=True)

    def output_detail(self):
        mensaje = ""
        detalle_str = "{cantidad} {producto} ${precio}"
        for detalle in self.detalles:
            mensaje += "-" + detalle_str.format(
                cantidad = detalle.cantidad,
                producto = detalle.producto,
                precio = detalle.precio_unitario
            ) + "\n"
        
        return mensaje[:-1]

    def calcula_total(self):
        self.total = sum([detalle.cantidad * detalle.precio_unitario for detalle in self.detalles])