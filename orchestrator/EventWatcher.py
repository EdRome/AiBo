import logging
from typing import Tuple, Any, Dict
from config.utils import pick_random_number

logger = logging.getLogger(__name__)

class Watcher:

    def execute(self, memory, action) -> Tuple[Any, Any, Any, Any]:
        logger.info("Ejecutando Watcher")
        recordatorio = False
        return_obj = {}
        # Valida que la acción sea recordatorio
        if isinstance(action, list):
            # En caso de ser una lista, valida en toda la lista si hubo algún recordatorio
            recordatorio = any([a == 'recordatorios' for a in action])
        else:
            recordatorio = action == 'recordatorios'
        
        if recordatorio:
            return_obj = self.valida_credenciales_google(memory)

        return return_obj.get('memory', memory), return_obj.get('mensaje', {}), return_obj.get('transicion', ''), return_obj.get('intention', '')

    def valida_credenciales_google(self, memory) -> Dict:
        logger.info("Validando y enviando mensaje para conexión a google calendar")
        return_obj = {}
        try:
            # Si el usuario no se ha registrado, envía mensaje con opción para registrarse
            if not memory.global_memory.request_google_calendar:
                num = pick_random_number(1,3)
                memory.global_memory.request_google_calendar = True
                if memory.global_memory.nombre_emprendedor == "":
                    num = 3
                    return_obj['mensaje'] = {'state': memory.user_id}
                else:
                    if num != 3:
                        return_obj['mensaje'] = {'state': memory.user_id, 'nombre': memory.global_memory.nombre_emprendedor}
                    else:
                        return_obj['mensaje'] = {'state': memory.user_id}

                return_obj['transicion'] = "conectar_calendario_" + str(num)
                return_obj['memory'] = memory
                return_obj['intention'] = 'recordatorios'
        except Exception as e:
            logger.error(f"Error al validar credenciales de google: {e}")

        return return_obj