import logging
from ..llm.extractor import get_onboarding_data

logger = logging.getLogger(__name__)

class Bienvenida:

    def execute(self, memory, message: str, image: bytes = None, db_session=None, current_date=None):
        logger.info("Iniciando bienvenida")
        return_obj = {}
        try:

            onboarding_data = self._process_onboarding_text(memory, message, current_date)
            nombre = onboarding_data.nombre or memory.global_memory.nombre_emprendedor
            ultimo_mensaje = memory.local_state['bienvenida']['message'][-1]
            num_mensajes = len(memory.local_state['bienvenida']['message'])
            if (nombre is None or nombre == "") and num_mensajes == 1:
                # Primer mensaje, envía transición
                return_obj['transicion'] = 'transicion'
            elif nombre is not None and num_mensajes == 1:
                # Transicion proactiva
                return_obj['transicion'] = 'transicion_proactiva'
                return_obj['mensaje'] = {"nombre_emprendedor": nombre}
                memory.global_memory.nombre_emprendedor = nombre
            elif nombre is not None and ultimo_mensaje.lower() not in ['ok','listo','ready','vamos']:
                # Pasamos a micro mision ok
                return_obj['transicion'] = "mision_ok"
                return_obj['mensaje'] = {"nombre_emprendedor": nombre}
            elif nombre is not None and ultimo_mensaje.lower() in ['ok','listo','ready','vamos']:
                # Envía mensaje de tutorial y termina bienvenida
                return_obj['transicion'] = "menu_tutorial"

        except Exception as e:
            logger.error(f"Error durante la bievenida: {e}")
            return_obj['transicion'] = "error_bienvenida"

        return_obj['memory'] = memory
        return return_obj
    
    def _process_onboarding_text(self, memory, message, current_date):
        logger.info("Procesando texto de bienvenida")
        onboarding_data = get_onboarding_data(message, current_date)

        return onboarding_data