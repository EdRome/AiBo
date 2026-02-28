from pydantic import BaseModel

class SalesSummary(BaseModel):
    phone_number: str
    venta_total: float
    unidades_vendidas: int
    num_ventas: int