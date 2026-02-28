from statemachine import StateMachine, State
from data.models.memory.memory import Memory
from whatsapp.send_message.send_message import send_whatsapp_message
from typing import Optional

class InventoryMachine(StateMachine):
    """
    Máquina de estados para Registro de Inventario.
    Flow: Product -> Stock -> Confirm
    """
    
    # Estados
    waiting_product = State(initial=True)
    waiting_stock = State()
    confirming_update = State()
    finished = State(final=True)
    
    # Transiciones
    process_message = (
        waiting_product.to.itself() | 
        waiting_stock.to.itself() | 
        confirming_update.to.itself()
    )
    
    got_product = waiting_product.to(waiting_stock)
    got_stock = waiting_stock.to(confirming_update)
    confirmed = confirming_update.to(finished)
    cancelled = confirming_update.to(finished)
    
    def __init__(self, memory: Memory, message: Optional[str] = None):
        self.memory = memory
        self.user_message = message or ""
        self.inv_state = memory.local_state.inventario
        self.next_context = None
        super().__init__()
        
    def on_enter_waiting_product(self):
        # Si es el primer mensaje, preguntar producto
        if not self.inv_state.product:
            if not self.inv_state.aibo_message or "producto" not in self.inv_state.aibo_message[-1]:
                msg = "Para registrar inventario, ¿qué producto quieres actualizar?"
                send_whatsapp_message(self.memory.user_id, msg)
                self.inv_state.aibo_message.append(msg)

    def waiting_waiting_product(self, message: str):
        if message:
            self.inv_state.product = message
            self.got_product()

    def on_enter_waiting_stock(self):
        msg = f"¿Cuál es la nueva existencia de {self.inv_state.product}?"
        send_whatsapp_message(self.memory.user_id, msg)
        self.inv_state.aibo_message.append(msg)

    def waiting_waiting_stock(self, message: str):
        import re
        numbers = re.findall(r'\d+', message)
        if numbers:
            self.inv_state.stock = int(numbers[0])
            self.got_stock()
        else:
            msg = "Por favor ingresa un número válido."
            send_whatsapp_message(self.memory.user_id, msg)
            self.inv_state.aibo_message.append(msg)

    def on_enter_confirming_update(self):
        msg = f"Confirma actualizar inventario: {self.inv_state.product} a {self.inv_state.stock} unidades. Responde SI para confirmar o NO para cancelar."
        send_whatsapp_message(self.memory.user_id, msg)
        self.inv_state.aibo_message.append(msg)

    def waiting_confirming_update(self, message: str):
        msg = message.lower().strip()
        if msg in ["si", "sí", "yes", "confirmar"]:
            send_whatsapp_message(self.memory.user_id, "Inventario actualizado exitosamente.")
            self.inv_state.product = None
            self.inv_state.stock = None
            self.next_context = "Menu"
            self.confirmed()
        elif msg in ["no", "cancelar"]:
            send_whatsapp_message(self.memory.user_id, "Actualización cancelada.")
            self.inv_state.product = None
            self.inv_state.stock = None
            self.next_context = "Menu"
            self.cancelled()
        else:
            send_whatsapp_message(self.memory.user_id, "Responde SI o NO.")

    def get_next_context(self):
        return self.next_context
