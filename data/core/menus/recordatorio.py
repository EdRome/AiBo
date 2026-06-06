from pydantic import BaseModel, Field
from typing import Optional, List

class Recordatorio(BaseModel):
    active: bool = Field(default=False)
    step: str = Field(default="waiting_remainder")
    user_message: List[str] = Field(default_factory=list)
    aibo_message: List[str] = Field(default_factory=list)

    borrar_recordatorio: bool = Field(default=False)
    procesar_recordatorio: bool = Field(default=False)

    id_ultimo_recordatorio: int|List[int] = Field(default=0)

    message_type: str
    intention: str

    def is_waiting_remainder(self) -> bool:
        return self.step == "waiting_remainder"
    
    def is_remainder_created(self) -> bool:
        return self.step == "remainder_created"

    def get_full_user_message(self):
        return "\n".join(self.user_message)