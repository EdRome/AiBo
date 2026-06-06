from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class GlobalMemory(BaseModel):
    nombre_emprendedor: str = Field(default="")
    nombre_negocio: str = Field(default="")
    language: str = Field(strict=True, default="es", validate_default=True)

class Memory(BaseModel):
    user_id: str = Field(strict=True, default="", validate_default=True)
    active_context: str = Field(strict=True, default="", validate_default=True)
    machine_stack: List[str] = Field(strict=True, default=[], validate_default=True)
    global_memory: GlobalMemory = Field(strict=True, default=GlobalMemory(), validate_default=True)
    local_state: Dict
    last_interaction: datetime
    task_name: str = Field(strict=True, default="", validate_default=True)
    creditos_disponibles: int = Field(strict=True, default=20, validate_default=True)
    temporary_context: Optional[Dict[str, Any]] = None

    def restar_credito(self, creditos: int):
        self.creditos_disponibles -= creditos

    def reset_active_context(self):
        # Reinicia contexto actual
        context = self.local_state[self.active_context]
        context['message'] = []
        context['message_type'] = ""
        context['intention'] = ""
        
        try:
            # Reinicia estado IDLE
            idle_context = self.local_state['IDLE']
            idle_context['message'] = []
            idle_context['message_type'] = ""
            idle_context['intention'] = ""
        except:
            self.add_new_local_state("IDLE")

        self.active_context = "IDLE"

    def add_new_local_state(self, state):
        self.local_state[state] = {
            'message': [],
            'message_type': "",
            "intention": ""
        }

    def get_message(self):
        return "\n".join(self.local_state[self.active_context]['message'])

    def append_message(self, message: str):
        try:
            self.local_state[self.active_context]['message'].append(message)
        except:
            self.local_state[self.active_context] = {
                'message': [message],
                'message_type': "",
                'intention': ""
            }

    def update_message_type(self, value):
        self.local_state[self.active_context]['message_type'] = value

    def update_intention(self, value):
        self.local_state[self.active_context]['intention'] = value

    def get_intention(self) -> str:
        return self.local_state[self.active_context]['intention']
    
    def get_message_type(self) -> str:
        return self.local_state[self.active_context]['message_type']

    def update_last_interaction(self, last_interaction=None):
        self.last_interaction = last_interaction or datetime.now()
