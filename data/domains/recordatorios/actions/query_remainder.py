import logging

from ..llm import get_remainder_query_extractor
from ..repository import get_remainder_by_criteria

logger = logging.getLogger(__name__)

class QueryRemaindersAction:

    def execute(self, memory, message: str, image = None, db_session=None, current_date=None):
        logger.info("Consultando recordatorios")
        return_obj = {}
        try:
            remainder_query = get_remainder_query_extractor(message, current_date)
            if remainder_query is not None and remainder_query['start_date'] == '1900-12-31' and remainder_query['end_date'] == '1900-12-31':
                raise Exception("Error en la consulta de ventas")
            remainders = get_remainder_by_criteria(
                memory.user_id, 
                remainder_query["start_date"], 
                remainder_query["end_date"], 
                remainder_query["search_query"], 
                db_session
            )

            return_obj['mensaje'] = remainders
            return_obj['transicion'] = "confirmacion_consulta" if len(remainders['lista_recordatorios']) > 0 else "cero_consulta"
                
        except Exception as e:
            logger.error(f"Error al consultar recordatorios: {e}")
            return_obj['transicion'] = "error_consulta"
        
        return_obj['memory'] = memory
        return return_obj