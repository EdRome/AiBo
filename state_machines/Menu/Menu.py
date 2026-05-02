import logging
from data.models.memory.memory import Memory
from whatsapp.send_message.send_message import send_whatsapp_message, send_whatsapp_template
from whatsapp.messages.multiidioma import MultiIdioma
from utils import build_progress_bar

logger = logging.getLogger(__name__)

class MenuMachine():
    """
    Clase encargada exclusivamente de la interfaz de usuario y navegación.
    Actúa como la "Vista" en un patrón MVC simplificado
    """

    def __init__(self, memory: Memory, idioma: MultiIdioma = None):
        self.memory = memory
        # Si no se provee idioma, se recupera de la memoria global
        self.idioma = idioma if idioma else MultiIdioma(memory.global_memory.language)

    def display_main_menu(self):
        """Muestra el menú de inicio rápido y resetea el estado a 'menú."""
        logger.info("3.1. Mostrando menú principal")
        send_whatsapp_template(
            self.memory.user_id,
            self.idioma.obtener('MENU_INICIO_RAPIDO')
        )
        self.memory.local_state.change_status('menu', True)
        self.memory.local_state.menu.user_message = []
        self.memory.local_state.menu.aibo_message = []

    def on_enter_venta(self):
        """Inicia visualmente el flujo de venta."""
        logger.info("3.2. Iniciando flujo de venta")
        mensaje = self.idioma.obtener("MENSAJE_INICIO_VENTA")
        send_whatsapp_template(
            self.memory.user_id,
            mensaje
        )
        
        self.memory.local_state.change_status('ventas', True)
        self.memory.local_state.ventas.aibo_message.append(mensaje)
        self.memory.local_state.ventas.procesar_venta = True
        self.memory.local_state.ventas.step = "registrar_venta"

    def on_enter_gasto(self):
        """Inicia visualmente el flujo de gasto."""
        logger.info("3.4. Iniciando flujo de gasto")
        mensaje = self.idioma.obtener("MENSAJE_INICIO_GASTO")
        send_whatsapp_message(
            self.memory.user_id,
            mensaje
        )

        self.memory.local_state.change_status('gastos', True)
        self.memory.local_state.gastos.aibo_message.append(mensaje)
        self.memory.local_state.gastos.procesar_gasto = True
        self.memory.local_state.gastos.step = 'registrar_gasto'

    def on_enter_recordatorio(self):
        """Inicia visualmente el flujo de recordatorio."""
        logger.info("3.5. Iniciando flujo de recordatorio")
        
        send_whatsapp_message(
            self.memory.user_id,
            "AiBo_Preparado.webp",
            is_image=True
        )

        mensaje = self.idioma.obtener("MENSAJE_INICIO_RECORDATORIO")
        send_whatsapp_message(
            self.memory.user_id,
            mensaje
        )

        self.memory.local_state.change_status('recordatorio', True)
        self.memory.local_state.recordatorio.aibo_message.append(mensaje)
        self.memory.local_state.recordatorio.procesar_recordatorio = True
        self.memory.local_state.recordatorio.step = 'crear_recordatorio'

    def on_enter_borrar_venta(self):
        """Inicia visualmente el flujo de borrado."""
        logger.info("3.3. Iniciando flujo de borrado")
        self.memory.local_state.change_status('ventas', True)
        self.memory.local_state.ventas.borrar_venta = True
        self.memory.local_state.ventas.step = "borrar_venta"
        mensaje = self.idioma.obtener("MENSAJE_CONFIRMACION_BORRAR_VENTA")
        send_whatsapp_template(self.memory.user_id, mensaje)

    def on_enter_onboarding(self):
        """Iniciando visualmente el flujo de onboarding"""
        # logger.ingo("Iniciando flujo de onboarding")
        # self.memory.local_state.change_status('onboarding', True)
        # self.memory.local_state.
        pass

    def show_feature_missing(self):
        """Notifica sobre funcionalidades aún no implementadas."""
        logger.info("3.4. Mostrando funcionalidad faltante")
        send_whatsapp_message(
            self.memory.user_id,
            self.idioma.obtener('MENSAJE_FUNCIONALIDAD_FALTANTE')
        )
        self.display_main_menu()

    def show_error(self, error_key='MENSAJE_ERROR_REGISTRO_VENTA'):
        """Muestra un mensaje de error genérico al usuario."""
        logger.info("3.5. Mostrando mensaje de error")
        send_whatsapp_message(
            self.memory.user_id,
            self.idioma.obtener(error_key)
        )
        self.display_main_menu()

    def show_progress(self, memory_state, ultima_accion):
        """Muestra un mensaje con el progreso del usuario."""
        logger.info("3.6. Mostrando progreso")
        barra = build_progress_bar(memory_state.progreso_nivel)
        barra = barra + f" {memory_state.progreso_nivel}%"

        send_whatsapp_message(
            self.memory.user_id,
            self.idioma.obtener(
                "MENSAJE_PROGRESO", 
                datos={
                    "exp": 25,
                    "accion_realizada": ultima_accion,
                    "nivel_actual": memory_state.nivel_actual,
                    "barra_progreso": barra,
                    "progreso": "\n".join(memory_state.misiones),
                    "siguiente_nivel": memory_state.siguiente_nivel
                }
            )
        )

    def show_next_level(self, memory_state):
        send_whatsapp_message(
            self.memory.user_id,
            self.idioma.obtener(
                "LEVEL_UP",
                datos={
                    "nivel": memory_state.nivel_actual
                }
            )
        )