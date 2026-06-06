import logging

logger = logging.getLogger(__name__)

def retrieve_user_message_content(memory):
    try:
        image = None
        full_message = None
        message_type = None
        intent = None

        active_state = memory.local_state.get_active_state()

        if active_state:
            state_obj = getattr(memory.local_state, active_state)
            if hasattr(state_obj, 'is_image') and state_obj.is_image():
                image = state_obj.get_image_content()
            else:
                full_message = state_obj.get_full_user_message()
            
            message_type = active_state.message_type
            intent = active_state.intention
            
        return image, full_message, message_type, intent
    except Exception as e:
        logger.error(f"Error al recuperar el contenido del mensaje del usuario: {e}")
        return None, None, None, None

def build_progress_bar(progreso: int):
    """La barra se compone de 10 barras
    Para progresos entero (10, 20, 30, etc.), el último rectangulo es la barra llena
    Para progresos que terminan en 5 (5, 15, 25, etc.), el último rectangulo es la barra medio llena

    El progreso se calcula como 
    progreso_entero = int(progreso/10)
    progreso_medio = int(progreso%10 == 5)
    progreso_restante = total_rectangulos - progreso_entero - progreso_medio

    barra_llena * progreso_entero + barra_medio_llena * progreso_medio + barra_vacia * progreso_restante
    """

    barra_vacia = "░" # Para 0%
    barra_llena = "█" # Para números enteros
    barra_medio_llena = "▓" # Para números que terminan en 5

    total_rectangulos = 10
    progreso_entero = int(progreso/total_rectangulos)
    progreso_medio = int((progreso%total_rectangulos) == 5)
    progreso_restante = total_rectangulos - progreso_entero - progreso_medio

    barra_progreso = barra_llena * progreso_entero + barra_medio_llena * progreso_medio + barra_vacia * progreso_restante
    return barra_progreso
