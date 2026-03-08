import logging
from llm.core.entity_extractor import get_intention
from whatsapp.messages.multiidioma import MultiIdioma
from actions.create_sales_action import CreateSalesAction
from actions.delete_sales_action import DeleteSalesAction
from state_machines.Menu.Menu import MenuMachine

class WorkflowOrchestrator:
    def __init__(self, memory):
        self.memory = memory
        self.idioma = MultiIdioma(memory.global_memory.language)

        self.menu_ui = MenuMachine(self.memory, self.idioma)

        # Registro de acciones, cuando se agregue una nueva accion se debe agregar aqui
        self.actions = {
            'registrar_venta': CreateSalesAction(self.idioma),
            'borrar_venta': DeleteSalesAction(self.idioma)
        }

    def process(self, message: str = None, image: bytes = None):
        """
        Punto de entrada principal para procesar cualquier mensaje entrante
        """
        active_state = self.memory.local_state.active_state

        # 1. Determinar la intención del usuario
        intent = self._get_effective_intent(active_state, message)
        logger.info(f"Intención efectiva detectada: {intent}")

        # 2. Ejecutar el Action correspondiente
        if intent in self.actions:
            return self.actions[intent].execute(self.memory, message, image)
        
        # 3. Manejar transiciones de estado y UI (MenuMachine)
        self._handle_ui_transitions(intent)

    def _get_effective_intent(self, active_state, message):
        """
        Si el usuario está en un estado específico (ej. ventas), mantenemos ese flujo.
        Si está en el menú o estado neutro, extraemos la intención con LLM.
        """
        # Si el usuario ya está dentro de un flujo, el estado manda
        if active_state and active_state != 'menu':
            return active_state

        # Si está en el menú, usamos el LLM para saber a dónde quiere ir
        if message:
            return get_intention(message)

        return 'menu'

    def _should_execute_action(self, active_state):
        """
        Valida si ya estamos en un estado de procesamiento.
        Por ejemplo, si el estado es 'ventas', el Action ya puede ejecutarse.
        """
        return active_state == 'ventas'

    def _handle_ui_transitions(self, intent):
        """
        Usa MenuMachine para mover al usuario entre pantallas según su intención.
        """
        if intent == 'registrar_venta':
            self.menu_ui.on_enter_venta()

        elif intent == 'borrar_venta':
            self.menu_ui.on_enter_borrar_venta()
        
        elif intent == 'menu':
            self.menu_ui.display_main_menu()

        elif intent in ['registrar_inventario', 'otras_acciones']:
            self.menu_ui.show_feature_missing()

        else:
            # Si no entiende la intención, regresa al menú por seguridad
            self.menu_ui.display_main_menu()