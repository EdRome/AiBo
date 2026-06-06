import logging
from cloud_task.cloud_task import schedule_remainder_task
from ..repository import insert_remainder
from ..llm.extractor import get_remainder_data

logger = logging.getLogger(__name__)

class CreateRemaindersAction:

    # def __init__(self, idioma):
    #     self.idioma = idioma

    def execute(self, memory, message: str, image: bytes = None, db_session=None, current_date=None):
        logger.info("Creando recordatorios")
        return_obj = {}

        try:
            logger.info("2.2. Procesando información del recordatorio...")
            recordatorios = self._process_remainder_text(memory, message, current_date)
            _ = [insert_remainder(recordatorio, db_session) for recordatorio in recordatorios]

            return_obj['transicion'] = "confirmacion_registro"
            return_obj['mensaje'] = {
                "lista_detalle": "\n".join(["-" + recordatorio.recordatorio + " " + recordatorio.fecha_recordatorio.strftime("%d-%m-%Y %H:%M") for recordatorio in recordatorios])
            }
        except Exception as e:
            logger.error(f"Error al crear recordatorios: {e}")
            return_obj['transicion'] = "error_registro"

        return_obj['memory'] = memory
        return return_obj

    def _process_remainder_text(self, memory, message, current_date):
        logger.info("2.2.1. Procesando texto del recordatorio...")
        try:
            remainder_data = get_remainder_data(message, memory.user_id, current_date)
            for recordatorio in remainder_data:
                task_id = schedule_remainder_task(
                    memory.user_id, 
                    recordatorio.fecha_recordatorio,
                    recordatorio.recordatorio
                )
                recordatorio.task_id = task_id
                recordatorio.calcula_delta()
            
            return remainder_data
        except Exception as e:
            logger.error(f"Error al procesar el texto del recordatorio {e}")
            return None


