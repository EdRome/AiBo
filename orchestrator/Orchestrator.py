import logging
from llm.core.entity_extractor import get_intention
from whatsapp.messages.multiidioma import MultiIdioma
from actions.create_sales_action import CreateSalesAction
from actions.delete_sales_action import DeleteSalesAction
from actions.onboarding_step1_action import OnboardingStep1
# from actions.create_remainders_action import CreateRemaindersAction
from state_machines.Menu.Menu import MenuMachine

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    def __init__(self, memory):
        self.memory = memory
        self.idioma = MultiIdioma(memory.global_memory.language)

        self.menu_ui = MenuMachine(self.memory, self.idioma)

        # Registro de acciones, cuando se agregue una nueva accion se debe agregar aqui
        self.actions = {
            # 'registrar_recordatorio': CreateRemaindersAction(self.idioma),
            'registrar_venta': CreateSalesAction(self.idioma),
            'borrar_venta': DeleteSalesAction(self.idioma),
            'onboarding': OnboardingStep1(self.idioma)
        }

        self.action_map = {
            'registrar_venta': self.menu_ui.on_enter_venta,
            # 'registrar_recordatorio': self.menu_ui.on_enter_recordatorio,
            'borrar_venta': self.menu_ui.on_enter_borrar_venta,
            'menu': self.menu_ui.display_main_menu,
            'registrar_inventario': self.menu_ui.show_feature_missing,
            'otras_acciones': self.menu_ui.show_feature_missing
        }

    def process(self, message: str = None, image: bytes = None):
        """
        Punto de entrada principal para procesar cualquier mensaje entrante
        """
        # 1. Obtener estado activo
        active_state = self.memory.local_state.get_active_state()

        if (active_state and active_state == 'menu') or not active_state:
            # 1.1 Determina la intención del usuario. Solo si estoy en el menu o no hay estado activo
            intent = self._get_effective_intent(active_state, message)
            # 1.2 Manejar transiciones de estado y UI (MenuMachine)
            self._handle_ui_transitions(intent)
    
        # 2. Ejecutar el Action correspondiente
        elif active_state and active_state != 'menu':
            active_obj = getattr(self.memory.local_state, active_state)
            self.memory = self.actions[active_obj.step].execute(self.memory, message, image)
            self._reset_menu_buffer()

    def _get_effective_intent(self, active_state, message):
        """
        Si el usuario está en un estado específico (ej. ventas), mantenemos ese flujo.
        Si está en el menú o estado neutro, extraemos la intención con LLM.
        """
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
        logger.info("3. Manejando transiciones de estado y UI")
        self.action_map.get(intent, self.menu_ui.display_main_menu)()

    def _reset_menu_buffer(self):
        self.memory.local_state.change_status('menu', True)
        self.memory.local_state.menu.user_message = []
        self.memory.local_state.menu.aibo_message = []