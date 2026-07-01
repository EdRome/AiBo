import logging
from interfaces.action import Action
from ..llm.extractor import confirm_delete
from ..repository import borrar_venta
from core.services.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DeleteSalesAction(Action):
    def __init__(self, idioma):
        self.idioma = idioma

    def execute(self, memory, message: str = None, image: bytes = None, db_session=None):
        """
        Valida la confirmación del usuario y elimina la última venta registrada
        Args:
            memory: Objeto Memory que contiene el estado de la conversación
            message: Mensaje de texto del usuario
            image: Imagen enviada por el usuario (no se usa, solo por compatibilidad con Action)
        Returns:
            Objeto Memory actualizado
        """
        try:
            # Recupera el último mensaje del usuario para confirmar la intención de borrado
            last_message = message if message else (
                memory.local_state.ventas.user_message[-1]
                if memory.local_state.ventas.user_message else ""
            )

            if confirm_delete(last_message):
                # Intenta borrar la venta usando el ID almacenado
                id_venta = memory.local_state.ventas.id_ultima_venta
                exito = borrar_venta(id_venta, memory.user_id, db_session)

                if exito:
                    send_whatsapp_message(
                        memory.user_id,
                        self.idioma.obtener('MENSAJE_VENTA_BORRADA_CORRECTAMENTE'),
                        db_session=db_session
                    )
                else:
                    send_whatsapp_message(
                        memory.user_id,
                        self.idioma.obtener('MENSAJE_ERROR_REGISTRO_VENTA'),
                        db_session=db_session
                    )
            else:
                # Si el LLM no confirma el borrado, notificamos al usuario
                logger.info("Borrado cancelado por el usuario o falta de confirmación clara.")
        
        except Exception as e:
            logger.error(f"Error en DeleteSalesAction: {str(e)}")
            send_whatsapp_message(
                memory.user_id,
                self.idioma.obtener('MENSAJE_ERROR_REGISTRO_VENTA'),
                db_session=db_session
            )

        # Finaliza el flujo regresando al menú principal
        return self._reset_to_menu(memory)

    def _reset_to_menu(self, memory):
        """ Limpia el estado de borrado y muestra el menú principal"""
        memory.local_state.change_status('menu', True)
        memory.local_state.ventas.borrar_venta = False
        memory.local_state.ventas.user_message = []
        memory.local_state.ventas.aibo_message = []
        memory.local_state.menu.user_message = []
        memory.local_state.ventas.step = "waiting_product"
        return memory