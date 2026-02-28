from pydantic import BaseModel, Field
from typing import Optional, List

class Venta(BaseModel):
    # Campos de estado de la máquina
    active: bool = Field(default=False)
    step: str = Field(default="waiting_product")
    product: Optional[str] = None
    quantity: Optional[int] = None
    
    # Historial de mensajes (para compatibilidad con executor genérico)
    user_message: List[str] = Field(default_factory=list)
    aibo_message: List[str] = Field(default_factory=list)
    
    borrar_venta: bool = Field(default=False)
    procesar_venta: bool = Field(default=False)

    id_ultima_venta: int = Field(default=0)