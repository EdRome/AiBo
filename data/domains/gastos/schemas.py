from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List

class DetalleGastoBase(BaseModel):
    producto: str = Field(default="")
    cantidad: int = Field(default=1)
    precio_unitario: float = Field(default=0.0)

class DetalleGastoCreate(DetalleGastoBase):
    pass

class DetalleGasto(DetalleGastoBase):
    model_config = ConfigDict(from_attributes=True)

class ExpenseSummary(BaseModel):
    phone_number: str
    gasto_total: float
    unidades_gastadas: int
    num_gastos: int

class GastoBase(BaseModel):
    metodo_pago: str = Field(default="efectivo")
    total: float = Field(default=0.0)

class GastoCreate(GastoBase):
    detalles: List[DetalleGastoCreate]

class Gasto(GastoBase):
    phone_number: str
    fecha: datetime = Field(default=datetime.now())
    created_at: datetime = Field(default=datetime.now())
    detalles: List[DetalleGasto]
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

class BatchGastos(BaseModel):
    gasto: List[Gasto]

    def output_detail(self):
        mensaje = ""
        detalle_str = "{cantidad} {producto} ${precio}"
        for registro in self.gasto:
            for detalle in registro.detalles:
                mensaje += "-" + detalle_str.format(
                    cantidad = detalle.cantidad,
                    producto = detalle.producto,
                    precio = detalle.precio_unitario
                ) + "\n"
        return mensaje[:-1]

    def calcula_total(self):
        return sum([detalle.cantidad * detalle.precio_unitario for registro in self.gasto for detalle in registro.detalles])