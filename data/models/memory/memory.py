from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List
from data.models.etapa1.negocio import DatosNegocio
from data.models.menu.venta import Venta
from data.models.menu.gastos import Gasto
from data.models.menu.inventario import Inventario
from data.models.menu.recordatorio import Recordatorio
from data.models.menu.etapa1 import Etapa1

class GenericResult(BaseModel):
    aibo_message: List[str] = Field(strict=True, default=[], validate_default=True)
    user_message: List[str] = Field(strict=True, default=[], validate_default=True)
    llm_response: str = Field(strict=True, default="", validate_default=True)
    active: bool = Field(strict=True, default=False, validate_default=True)

    def get_full_user_message(self) -> str:
        return "\n".join(self.user_message)

class GlobalMemory(BaseModel):
    datos_negocio: DatosNegocio = Field(strict=True, default=DatosNegocio(), validate_default=True)
    language: str = Field(strict=True, default="es", validate_default=True)

class LocalState(BaseModel):
    etapa1: Etapa1 = Field(strict=True, default=Etapa1(), validate_default=True)
    ventas: Venta = Field(strict=True, default=Venta(), validate_default=True)
    gastos: Gasto = Field(strict=True, default=Gasto(), validate_default=True)
    inventario: Inventario = Field(strict=True, default=Inventario(), validate_default=True)
    recordatorio: Recordatorio = Field(strict=True, default=Recordatorio(), validate_default=True)
    menu: GenericResult = Field(strict=True, default=GenericResult(), validate_default=True)
    

    def get_active_state(self) -> str:
        for state_name in self.model_dump().keys():
            state_obj = getattr(self, state_name)
            if state_obj.active:
                return state_name
        return None

    def get_active_state_obj(self):
        for state_name in self.model_dump().keys():
            state_obj = getattr(self, state_name)
            if state_obj.active:
                return state_obj
        return None

    def change_status(self, state_name: str, status: bool):
        model = self.model_dump()
        for state in model.keys():
            if state == state_name:
                model[state]["active"] = status
            else:
                model[state]["active"] = False
        self.__init__(**model)

class Memory(BaseModel):
    user_id: str = Field(strict=True, default="", validate_default=True)
    active_context: str = Field(strict=True, default="", validate_default=True)
    machine_stack: List[str] = Field(strict=True, default=[], validate_default=True)
    global_memory: GlobalMemory = Field(strict=True, default=GlobalMemory(), validate_default=True)
    local_state: LocalState = Field(strict=True, default={}, validate_default=True)
    last_interaction: datetime = Field(strict=True, default_factory=lambda: datetime.now(), validate_default=True)
    task_name: str = Field(strict=True, default="", validate_default=True)
    creditos_disponibles: int = Field(strict=True, default=20, validate_default=True)

    def restar_credito(self, creditos: int):
        self.creditos_disponibles -= creditos

    def append_message(self, message: str):
        active_state = self.local_state.get_active_state_obj()
        if active_state is not None:
            active_state.user_message.append(message)