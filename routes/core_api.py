import os
import logging
from flask import Blueprint, jsonify, request, make_response
from data.config.database import get_db
from core.services.whatsapp import send_whatsapp_message
from data.domains.mensajes import insert_message, Message
from cloud_task.cloud_task import schedule_inactivity_task, delete_inactivity_task
from data.domains.memoria import Memory, GlobalMemory, get_memory, insert_memory, update_memory
from config.utils import get_current_date

logger = logging.getLogger(__name__)

core_api_bp = Blueprint('core_api', __name__)

@core_api_bp.route('/message', methods=['POST'])
def message():
    try:
        logger.info("Recibiendo mensaje")
        # 1. Acceder a los datos del formulario (req.formData())
        # request.form actúa como un diccionario con los datos del POST
        form_data = request.form

        # 2. Extraer los datos clave del mensaje
        raw_from = form_data.get('From', '')
        raw_to = form_data.get('To', '')
        body = form_data.get('Body', '')
        # Obtiene imagen
        media_url = form_data.get('MediaUrl0', '')
        # Detección de intención única
        message_type = form_data.get('MessageType', '') # Detecta si fue una interacción por botones
        intention = form_data.get('ButtonPayload', '') # Detecta la acción del botón

        # 3. Limpiar los strings (reemplazar 'whatsapp:+')
        sender = raw_from.replace('whatsapp:+', '')
        receiver = raw_to.replace('whatsapp:+', '')

        # 4. Convertir a un diccionario completo (Object.fromEntries)
        data = form_data.to_dict()

        message = Message(
            sender=sender, 
            receiver=receiver, 
            body=body, 
            data=data,
            multimedia=media_url
        )

        with get_db() as db:
            confirm = insert_message(message, db)
            if confirm is None or not confirm:
                return make_response(jsonify({
                    'status': 'error',
                    'message': 'Error al insertar el mensaje en la base de datos'
                }), 500)

            # Obtener o crear memoria del usuario
            memory = get_memory(sender, db)
            if memory is None:
                # Crear nueva memoria para usuario nuevo
                memory = Memory(
                    user_id=sender, 
                    active_context="bienvenida", 
                    machine_stack=[], 
                    global_memory=GlobalMemory(), 
                    local_state={}, 
                    last_interaction=get_current_date(),
                    task_name=""
                )
                language = "es"
                memory.global_memory.language = language
                insert_memory(memory, db)

            # Actualizar memoria existente con el nuevo mensaje
            logger.info(f"Estado activo {memory.active_context}")
            
            memory.append_message(body if not media_url else media_url)
            memory.update_last_interaction()
            memory.update_message_type(message_type)
            memory.update_intention(intention)

            if memory.task_name != "":
                delete_inactivity_task(task_name=memory.task_name)

            # Programar tarea de inactividad
            task_id = schedule_inactivity_task(sender)
            memory.task_name = task_id
            update_memory(memory, db)
        
        logger.info("Finalizando ejecución")
    except Exception as e:
        logger.error(f"Error al recibir el mensaje: {e}")
        send_whatsapp_message(sender, "Lo siento, hubo un error al recibir el mensaje")

    return make_response(jsonify({
        'status': 'success'
    }), 200)