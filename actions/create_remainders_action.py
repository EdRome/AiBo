import json
import logging
from llm.core.remainder_extractor import get_remainder_data
from interfaces.action import Action
from whatsapp.send_message.send_message import send_whatsapp_message, send_whatsapp_template
from data.db.remainders import insert_remainder, get_remainder_count
from cloud_task.cloud_task import schedule_remainder_task

logger = logging.getLogger(__name__)

class CreateRemaindersAction(Action):

    def __init__(self, idioma):
        self.idioma = idioma

    def execute(self, memory, message: str, image: bytes = None):
        logger.info("Creando recordatorios")
        recordatorio_id = None

        try:
            if memory.local_state.recordatorio.procesar_recordatorio:
                logger.info("2.2. Procesando información del recordatorio...")
                recordatorio = self._process_remainder_text(memory, message)
                recordatorio_id = insert_remainder(recordatorio)
                self._send_success_notification(memory, recordatorio_id)
        except Exception as e:
            logger.error(f"Error al crear recordatorios: {e}")
            send_whatsapp_message(memory.user_id, "Error al registrar el recordatorio")
            send_whatsapp_message(
                memory.user_id,
                "AiBo_Lo_Siento.webp",
                is_image=True
            )

        memory = self._reset_remainder_state(memory)
        return memory

    def _process_remainder_text(self, memory, message):
        logger.info("2.2.1. Procesando texto del recordatorio...")
        try:
            remainder_data = get_remainder_data(message, memory.user_id)
            logger.info(remainder_data.fecha_recordatorio)
            task_id = schedule_remainder_task(
                memory.user_id, 
                remainder_data.fecha_recordatorio,
                remainder_data.recordatorio
            )
            remainder_data.task_id = task_id
            remainder_data.calcula_delta()
            
            return remainder_data
        except Exception as e:
            logger.error(f"Error al procesar el texto del recordatorio")
            return None

    def _send_success_notification(self, memory, id_recodatorio):
        logger.info("Recordatorio registrado con exito.")
        try:

            message = "Recordatorio registrado!"
            memory.local_state.recordatorio.id_ultimo_recordatorio = id_recodatorio
            memory.local_state.recordatorio.aibo_message.append(message)
            send_whatsapp_message(memory.user_id, "AiBo_Listo.webp", is_image=True)
            send_whatsapp_message(memory.user_id, "Recordatorio registrado!")
        except Exception as e:
            logger.error(f"Error enviando notificación de registro exitoso de recordatorio {e}")

    def _reset_remainder_state(self, memory):
        logger.info("Reiniciando buffers")
        try:
            memory.local_state.change_status("menu", True)
            memory.local_state.recordatorio.procesar_recordatorio = False
            memory.local_state.recordatorio.user_message = []
            memory.local_state.recordatorio.aibo_message = []
            memory.local_state.recordatorio.step = "waiting_remainder"
            memory.local_state.menu.user_message = []
            return memory
        except Exception as e:
            logger.error(f"Error reiniciando los buffers {e}")
            return memory
