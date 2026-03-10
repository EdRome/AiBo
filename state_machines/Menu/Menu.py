import logging
from data.models.memory.memory import Memory
from whatsapp.send_message.send_message import send_whatsapp_message, send_whatsapp_template
from whatsapp.messages.multiidioma import MultiIdioma

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

    def on_enter_borrar_venta(self):
        """Inicia visualmente el flujo de borrado."""
        logger.info("3.3. Iniciando flujo de borrado")
        self.memory.local_state.change_status('ventas', True)
        self.memory.local_state.ventas.borrar_venta = True
        mensaje = self.idioma.obtener("MENSAJE_CONFIRMACION_BORRAR_VENTA")
        send_whatsapp_template(self.memory.user_id, mensaje)

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