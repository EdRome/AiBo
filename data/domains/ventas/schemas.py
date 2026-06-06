from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional

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

class SalesQueryExtraction(BaseModel):
    rango_solicitado: str = Field(
        ..., 
        description='Rango de la solicitud, puede ser: "hoy" | "ayer" | "esta_semana" | "semana_pasada" | "este_mes" | "mes_pasado" | "dia_especifico_semana" | "especifico"'
    )
    dia_semana: Optional[int] = Field(
        ..., 
        description='Día de específico de la semana, puede ser: null | int(0-6). Lunes es 0, domingo es 6'
    )
    relacion_semana: Optional[str] = Field(
        ..., 
        description='Relación con la semana actual, puede ser: null | "actual" | "pasada"'
    )
    mes_especifico: Optional[int] = Field(
        ...,
        description='Mes de análisis, puede ser: null | int (1-12)'
    )
    group_by: Optional[str] = Field(
        ...,
        description='Agrupación por periodo de tiempo, puede ser: "day" | "month" | null'
    )

class SaleSearchCriteria(BaseModel):
    start_date: Optional[str] = Field(
        None, 
        description="Fecha y hora de inicio calculada en formato ISO (YYYY-MM-DD HH:MM:SS)"
    )
    end_date: Optional[str] = Field(
        None, 
        description="Fecha y hora de fin calculada en formato ISO (YYYY-MM-DD HH:MM:SS)"
    )
    product_name: Optional[str] = Field(
        None, 
        description="Nombre del producto o palabra clave mencionada por el usuario"
    )

class SalesSelection(BaseModel):
    selected_numbers: List[int] = Field(
        ..., 
        description="Lista de números enteros seleccionados por el usuario (ej: [5, 10])"
    )