import logging
from cloud_task.cloud_task import schedule_remainder_task
from ..repository import insert_remainder
from ..llm.extractor import get_remainder_data
from config.utils import formatear_fecha_humana, pick_random_number, remainders_schedule
from core.services.google import crear_evento_calendario

logger = logging.getLogger(__name__)

class CreateRemaindersAction:

    def execute(self, memory, message: str, image: bytes = None, db_session=None, current_date=None):
        logger.info("Creando recordatorios")
        return_obj = {}

        try:
            logger.info("2.2. Procesando información del recordatorio...")
            remainder_data = self._process_remainder_text(memory, message, current_date)
            recordatorios = self._schedule_remainders(remainder_data, memory, current_date, db_session)
            _ = [insert_remainder(recordatorio, db_session) for recordatorio in recordatorios]

            num = pick_random_number()
            return_obj['transicion'] = f"confirmacion_registro_{str(num)}"
            return_obj['mensaje'] = {
                "lista_detalle": "\n".join(["-" + recordatorio.recordatorio + " " + formatear_fecha_humana(recordatorio.fecha_recordatorio) for recordatorio in recordatorios])
            }
        except Exception as e:
            logger.error(f"Error al crear recordatorios: {e}")
            return_obj['transicion'] = "error_registro"

        return_obj['memory'] = memory
        return_obj['action'] = 'recordatorios'
        return return_obj

    def _process_remainder_text(self, memory, message, current_date):
        logger.info("2.2.1. Procesando texto del recordatorio...")
        try:
            remainder_data = get_remainder_data(message, memory.user_id, current_date)            
            return remainder_data
        except Exception as e:
            logger.error(f"Error al procesar el texto del recordatorio {e}")
            return None

    def _schedule_remainders(self, remainder_data, memory, current_date, db_session):
        for recordatorio in remainder_data:
            first_remainder, type_first_remainder, second_remainder, type_second_remainder = \
                    remainders_schedule(recordatorio.fecha_recordatorio, current_date)

            humano_fecha_recordatorio = formatear_fecha_humana(recordatorio.fecha_recordatorio)
            if first_remainder is not None:
                schedule_remainder_task(
                    memory.user_id,
                    first_remainder,
                    recordatorio.recordatorio,
                    humano_fecha_recordatorio,
                    type_first_remainder
                )

            if second_remainder is not None:
                schedule_remainder_task(
                    memory.user_id,
                    second_remainder,
                    recordatorio.recordatorio,
                    humano_fecha_recordatorio,
                    type_second_remainder
                )

            task_id = schedule_remainder_task(
                memory.user_id, 
                recordatorio.fecha_recordatorio,
                recordatorio.recordatorio
            )
            recordatorio.task_id = task_id
            recordatorio.calcula_delta()

            _ = crear_evento_calendario(
                memory.user_id, 
                recordatorio.recordatorio, 
                recordatorio.fecha_recordatorio,
                recordatorio.fecha_recordatorio,
                db_session=db_session
            )
        
        return remainder_data