import logging
from interfaces.action import Action
from llm.core.entity_extractor import confirm_delete
from data.db.sales import borrar_venta
from whatsapp.send_message.send_message import send_whatsapp_message, send_whatsapp_template

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DeleteSalesAction(Action):
    def __init__(self, idioma):
        self.idioma = idioma

    def execute(self, memory, message: str = None):
        """
        Valida la confirmación del usuario y elimina la última venta registrada
        """
        try:
            # Recupera el último mensaje del usuario para confirmar la intención de borrado
            last_message = message if message else (
                memory.local_state.ventas.user_message[-1]
                if memory.local_state.ventas.user_message else ""
            )

            if confirm_delete(last_message):
                # Intenta borrar la venta usando el ID almacenado
                id_venta = memory.last_state.ventas.id_ultima_venta
                exito = borrar_venta(id_venta, memory.user_id)

                if exito:
                    send_whatsapp_message(
                        memory.user_id,
                        self.idioma.obtener('MENSAJE_VENTA_BORRADA_CORRECTAMENTE')
                    )
                else:
                    send_whatsapp_message(
                        memory.user_id,
                        self.idioma.obtener('MENSAJE_ERROR_REGISTRO_VENTA')
                    )
            else:
                # Si el LLM no confirma el borrado, notificamos al usuario
                logger.info("Borrado cancelado por el usuario o falta de confirmación clara.")
        
        except Exception as e:
            logger.error(f"Error en DeleteSalesAction: {str(e)}")
            send_whatsapp_message(
                memory.user_id,
                self.idioma.obtener('MENSAJE_ERROR_REGISTRO_VENTA')
            )

        # Finaliza el flujo regresando al menú principal
        self._reset_to_menu(memory)

    def _reset_to_menu(self, memory):
        """ Limpia el estado de borrado y muestra el menú principal"""
        memory.local_state.change_status('menu', True)
        memory.local_state.ventas.borrar_venta = False
        memory.local_state.ventas.user_message = []

        send_whatsapp_template(
            memory.user_id,
            self.idioma.obtener("MENU_INICIO_RAPIDO")
        )