from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List

class DetalleVentaBase(BaseModel):
    producto: str = Field(default="")
    cantidad: int = Field(default=1)
    precio_unitario: float = Field(default=0.0)

class DetalleVentaCreate(DetalleVentaBase):
    pass

class DetalleVenta(DetalleVentaBase):
    # venta_id : int
    model_config = ConfigDict(from_attributes=True)

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

class BatchVentas(BaseModel):
    venta: List[Venta]

    def output_detail(self):
        mensaje = ""
        detalle_str = "{cantidad} {producto} ${precio}"
        for registro in self.venta:
            for detalle in registro.detalles:
                mensaje += "-" + detalle_str.format(
                    cantidad = detalle.cantidad,
                    producto = detalle.producto,
                    precio = detalle.precio_unitario
                ) + "\n"
        return mensaje[:-1]

    def calcula_total(self):
        return sum([detalle.cantidad * detalle.precio_unitario for registro in self.venta for detalle in registro.detalles])

class SalesSummary(BaseModel):
    phone_number: str
    venta_total: float
    unidades_vendidas: int
    num_ventas: int