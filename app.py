import os
import logging
from datetime import timedelta

import pendulum
from flask_cors import CORS
from flask import Flask, jsonify, request, make_response

from orchestrator.Orchestrator import AiBoDirector
from cloud_task.cloud_task import schedule_inactivity_task, delete_inactivity_task, schedule_users_inactivity_review, schedule_descrubre_task
from data.domains.mensajes import insert_message, Message
from data.domains.conversacion import Descubre
from data.domains.memoria import Memory, GlobalMemory, get_memory, insert_memory, update_memory, get_2_more_days_last_interaction
from data.domains.recordatorios import get_remainder_by_task_id, update_remainder
from core.services.whatsapp import send_whatsapp_message, send_transition
from core.services.google import oauth_callback, generate_auth_url
from data.config.database import get_db, db_session
from config.utils import get_current_date, pick_random_number

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO) # O logging.DEBUG para ver todo
logger = logging.getLogger(__name__)

logger.info("Versión de la aplicación: 4.0")
numero_aibo = os.environ.get("TWILIO_WHATSAPP_NUMBER")

@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    Este método se ejecuta automáticamente al finalizar CADA solicitud HTTP,
    sin importar si fue exitosa o lanzó una excepción.
    """
    db_session.remove()  # Limpia la sesión del hilo y libera la conexión

@app.route('/descrube', methods=["POST"])
def descrube():
    try:
        data = request.get_json()
        sender = data.get('sender')
        message = data.get('message')

        with get_db() as db:
            memory = get_memory(sender, db)
            
            ultima_interaccion = pendulum.from_timestamp(memory.last_interaction.timestamp(), tz="America/Mexico_City")
            hoy = pendulum.from_timestamp(get_current_date().timestamp(), tz="America/Mexico_City")

            if ultima_interaccion.is_same_day(hoy):
                send_whatsapp_message(sender, message, False, db)
            else:
                logger.warning("El usuario no regreso a la herramienta")

    except Exception as e:
        logger.error(f"Error al enviar descrube {e}")

@app.route('/recurrencia', methods=["POST"])
def recurrencia():
    try:
        mensajes_descubre = Descubre()
        hoy = get_current_date()
        with get_db() as db:
            try:
                inactive_users = get_2_more_days_last_interaction(hoy, db)
                
                hace_dos_dias = hoy - timedelta(days=2) 
                hace_tres_dias = hoy - timedelta(days=3)
                hace_cuatro_dias = hoy - timedelta(days=4)
                hace_cinco_dias = hoy - timedelta(days=5)
                hace_seis_dias = hoy - timedelta(days=6)
                logger.info(f"Num inactive users {len(inactive_users)}")
                for user in inactive_users:
                    logger.info(f"Para la memoria {user.user_id}")
                    # Hace 2 días que no tiene interacción pero no más de 3 días
                    if hace_tres_dias < user.last_interaction <= hace_dos_dias:
                        send_transition(db, user.user_id, "interacciones", "dos_dias_sin_interaccion")
                        mensaje = mensajes_descubre.execute(None, None, None, db)['mensaje']
                        schedule_descrubre_task(user.user_id, mensaje)
                        logger.info("Hace 2 días que no tiene interacción pero no más de 3 días")

                    # Hace 3 días que no tiene interacción pero no más de 4 días
                    elif hace_cuatro_dias < user.last_interaction <= hace_tres_dias:
                        send_transition(db, user.user_id, "interacciones", "tres_dias_sin_interaccion")
                        logger.info("Hace 3 días que no tiene interacción pero no más de 4 días")

                    # Hace 4 días que no tiene interacción pero no más de 5 días
                    elif hace_cinco_dias < user.last_interaction <= hace_cuatro_dias:
                        send_transition(db, user.user_id, "interacciones", "cuatro_dias_sin_interaccion")
                        logger.info("Hace 4 días que no tiene interacción pero no más de 5 días")

                    # Hace 5 días o más que no tiene interacción
                    elif hace_seis_dias < user.last_interaction <= hace_cinco_dias:
                        num = pick_random_number(1,3)
                        send_transition(db, user.user_id, "interacciones", f"cinco_dias_sin_interaccion_{str(num)}")
                        logger.info("Hace 5 días o más que no tiene interacción")

                    logger.info("Enviando menú")
                    send_transition(db, user.user_id, "IDLE", None)
                    user.reset_active_context()
                    update_memory(user, db)
            except Exception as e:
                logger.error(f"Error al enviar mensaje de recurrencia {e}")

        schedule_users_inactivity_review()
    except Exception as e:
        logger.error(f"Error al enviar mensajes de recurrencia {e}")

    return make_response(jsonify({
        'status': 'success',
        'message': 'Recurrencia validada correctamente'
    }), 200)

@app.route('/oauth2callback', methods=["GET"])
def oauth2callback():
    code = request.args.get("code")
    user_id = request.args.get("state")
    try:
        if not code or not user_id:
            return make_response(jsonify({
                'status': 'sucess',
                'message': 'Parámetros insuficientes'
            }), 200)

        with get_db() as db:
            message = oauth_callback(code, user_id, get_current_date(), db)
            if message is not None:
                send_whatsapp_message(
                    user_id,
                    message,
                    db_session=db
                )
    except Exception as e:
        logger.error(f"Error durante el callback de oauth {e}")
    finally:
        wa_url = f"https://wa.me/{numero_aibo}"

        html = f"""<!doctype html>
    <html><head><meta charset="utf-8"></head>
    <body>
    <script>
    // Regresa al chat de WhatsApp
    window.location.replace("{wa_url}");

    // Fallback si el webview no permite la navegación
    setTimeout(function() {{
        window.location.replace("/oauth/success?ok=1");
    }}, 1000);
    </script>
    </body></html>"""

        return make_response(html, 200)

@app.route('/remainder', methods=['POST'])
def remainder():
    try:
        logger.info("Enviando recordatorio")
        data = request.get_json()
        sender = data.get('sender')
        message = data.get('message')
        task_id = data.get('task_id')
        fecha_recordatorio = data.get("fecha_final_recordatorio")
        tipo_recordatorio = data.get("tipo_recordatorio")

        with get_db() as db:
            remainder = get_remainder_by_task_id(task_id, db)
            if remainder is not None:
                remainder.status = 'completed'
                update_remainder(remainder)

            if fecha_recordatorio is not None and tipo_recordatorio is not None:
                send_transition(
                    db, sender, "recordatorios", tipo_recordatorio, **{"recordatorio": message, "fecha_recordatorio": fecha_recordatorio}
                )
            elif fecha_recordatorio is None and tipo_recordatorio is not None:
                send_transition(
                    db, sender, "recordatorios", tipo_recordatorio, **{"recordatorio": message}
                )
            else:
                send_transition(
                    db, sender, "recordatorios", "envia_recordatorio", **{"recordatorio": message}
                )

    except Exception as e:
        logger.error(f"Error al enviar el recordatorio: {e}")
        send_whatsapp_message(sender, "Lo siento, ocurrió un error al procesar el recordatorio")

    return make_response(jsonify({
        'status': 'success',
        'message': 'Recordatorio enviado correctamente'
    }), 200)

@app.route('/consume_message', methods=['POST'])
def consume_message():
    """
    Endpoint optimizado: Delega el procesamiento al WorkflowOrchestrator.
    """
    try:
        logger.info("1. Consumiendo mensaje con Orquestador")
        data = request.get_json()
        sender = data.get('sender')
        current_date = get_current_date()

        with get_db() as db:
            memory = get_memory(sender, db)
            if memory is None:
                return make_response(jsonify({'status': 'error', 'message': 'Error al obtener la memoria'}), 500)

            # Gestión de tareas de inactividad
            if memory.task_name:
                delete_inactivity_task(memory.task_name, sender)

            orchestador = AiBoDirector()
            memory = orchestador.execute_logic(memory, current_date, db)

            # Persistencia y tareas post-procesamiento
            update_memory(memory, db)
    
    except Exception as e:
        logger.error(f"Error al consumir el mensaje: {e}")
        send_whatsapp_message(sender, "Lo siento, hubo un error al procesar tu solicitud.")

    return make_response(jsonify({'status': 'success', 'message': 'Procesamiento completado'}), 200)

@app.route('/message', methods=['POST'])
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

# @app.route('/test', methods=['POST'])
def test():
    from core.services.google.client import leer_eventos
    from datetime import timedelta
    return_json = {}
    try:
        url = generate_auth_url('5215610910426')
        return_json['url'] = url
        # with get_db() as db:
        #     ahora = get_current_date()
        #     despues = ahora + timedelta(days=1)
        #     eventos = leer_eventos('5215528092514', ahora, despues, db)
        #     logger.info(eventos)
    except Exception as e:
        logger.error(e)
        return_json = {
            'status': 'error',
            'error': e
        }

    return make_response(jsonify(return_json), 200)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)