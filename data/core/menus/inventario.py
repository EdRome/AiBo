from pydantic import BaseModel, Field
from typing import Optional, List

class Inventario(BaseModel):
    # Campos de estado de la máquina
    active: bool = Field(default=False)
    step: str = Field(default="waiting_product")
    product: Optional[str] = None
    stock: Optional[int] = None
    
    # Historial de mensajes
    user_message: List[str] = Field(default_factory=list)
    aibo_message: List[str] = Field(default_factory=list)
