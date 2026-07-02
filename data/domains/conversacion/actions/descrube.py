import logging
from ..repository import get_mensaje_random

logger = logging.getLogger(__name__)

class Descubre:

    def execute(self, memory, message, image, db_session=None, current_date=None):
        logger.info("Iniciando descubre")
        return_obj = {}

        mensaje = get_mensaje_random(db_session)

        return_obj['mensaje'] = mensaje.mensaje

        return return_obj
