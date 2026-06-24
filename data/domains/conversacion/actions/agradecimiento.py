import logging
from config.utils import pick_random_number, pick_random_text

logger = logging.getLogger(__name__)

class Agradecimiento:

    def execute(self, memory, message: str, image: bytes = None, db_session=None, current_date=None):
        logger.info("Iniciando agradecimiento")
        return_obj = {}

        try:
            return_obj['transicion'] = message
        except Exception as e:
            logger.error(f"Error durante agradecimiento {e}")
            return_obj['transicion'] = 'error_agradecimiento'
        
        return return_obj