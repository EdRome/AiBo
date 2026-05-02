from pydantic import BaseModel

class ExpenseSummary(BaseModel):
    phone_number: str
    gasto_total: float
    unidades_gastadas: int
    num_gastos: int