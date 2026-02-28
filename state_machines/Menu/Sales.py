from statemachine import StateMachine, State
from data.models.memory.memory import Memory
from whatsapp.send_message.send_message import send_whatsapp_message
from typing import Optional

class SalesMachine(StateMachine):
    """
    Máquina de estados para Registro de Ventas.
    Flow: Product -> Quantity -> Confirm
    """
    
    # Estados
    waiting_product = State(initial=True)
    waiting_quantity = State()
    confirming_sale = State()
    finished = State(final=True)
    
    # Transiciones
    process_message = (
        waiting_product.to.itself() | 
        waiting_quantity.to.itself() | 
        confirming_sale.to.itself()
    )
    
    got_product = waiting_product.to(waiting_quantity)
    got_quantity = waiting_quantity.to(confirming_sale)
    confirmed = confirming_sale.to(finished)
    cancelled = confirming_sale.to(finished)
    
    def __init__(self, memory: Memory, message: Optional[str] = None):
        self.memory = memory
        self.user_message = message or ""
        self.sales_state = memory.local_state.ventas
        self.next_context = None
        super().__init__()
        
    def on_enter_waiting_product(self):
        # Si es el primer mensaje (entrada desde menú), preguntar producto
        if not self.sales_state.product:
            if not self.sales_state.aibo_message or "producto" not in self.sales_state.aibo_message[-1]:
                msg = "Para registrar la venta, ¿qué producto vendiste?"
                send_whatsapp_message(self.memory.user_id, msg)
                self.sales_state.aibo_message.append(msg)

    def waiting_waiting_product(self, message: str):
        if message:
            self.sales_state.product = message
            self.got_product()

    def on_enter_waiting_quantity(self):
        msg = f"¿Cuántos {self.sales_state.product} vendiste?"
        send_whatsapp_message(self.memory.user_id, msg)
        self.sales_state.aibo_message.append(msg)

    def waiting_waiting_quantity(self, message: str):
        # Intentar extraer número
        import re
        numbers = re.findall(r'\d+', message)
        if numbers:
            self.sales_state.quantity = int(numbers[0])
            self.got_quantity()
        else:
            msg = "Por favor ingresa un número válido."
            send_whatsapp_message(self.memory.user_id, msg)
            self.sales_state.aibo_message.append(msg)

    def on_enter_confirming_sale(self):
        msg = f"Confirma venta: {self.sales_state.quantity} x {self.sales_state.product}. Responde SI para confirmar o NO para cancelar."
        send_whatsapp_message(self.memory.user_id, msg)
        self.sales_state.aibo_message.append(msg)

    def waiting_confirming_sale(self, message: str):
        msg = message.lower().strip()
        if msg in ["si", "sí", "yes", "confirmar"]:
            send_whatsapp_message(self.memory.user_id, "Venta registrada exitosamente.")
            self.sales_state.product = None # Reset partial state
            self.sales_state.quantity = None
            self.next_context = "Menu" # Volver al menú
            self.confirmed()
        elif msg in ["no", "cancelar"]:
            send_whatsapp_message(self.memory.user_id, "Venta cancelada.")
            self.sales_state.product = None
            self.sales_state.quantity = None
            self.next_context = "Menu"
            self.cancelled()
        else:
            send_whatsapp_message(self.memory.user_id, "Responde SI o NO.")

    def get_next_context(self):
        return self.next_context
