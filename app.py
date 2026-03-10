import os
import logging

from flask_cors import CORS
from datetime import datetime
from flask import Flask, jsonify, request, make_response
from cloud_task.cloud_task import schedule_inactivity_task, delete_inactivity_task, schedule_sales_summary_task

from state_machines.executor import StateMachineExecutor
from state_machines.Onboarding.Etapa1 import Etapa1
# from state_machines.Menu.Menu import MenuMachine
from orchestrator.Orchestrator import WorkflowOrchestrator
from data.db.messages import insert_message
from data.models.sqlalchemy.messages import Message
from data.db.memory import get_memory, insert_memory
from data.models.memory.memory import Memory, GlobalMemory, LocalState, GenericResult
from data.db.sales import consulta_ventas_dia_actual
from state_machines.utils import creditos_casi_agotados, creditos_agotados
from whatsapp.messages.multiidioma import MultiIdioma
from whatsapp.send_message.send_message import send_whatsapp_message, send_whatsapp_template
from llm.core.summary_creator import create_summary

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO) # O logging.DEBUG para ver todo
logger = logging.getLogger(__name__)

logger.error("Versión de la aplicación: 2.0.1 alpha")

@app.route('/stripe_payment_status', methods=['POST'])
def stripe_payment_status():
    try:
        logger.error("Recibiendo estado de pago")
        data = request.get_json()
        body = data.get('body')
        logger.error(body)
        
    except Exception as e:
        logger.error(f'Error al recibir el estatus de pago {e}')
        return make_response(jsonify({
            'status': 'error',
            'message': 'Error al recibir el estatus de pago'
        }), 500)
    
    return make_response(jsonify({
        'status': 'success',
        'message': 'Estatus de pago recibido correctamente'
    }), 200)

@app.route('/sales_summary', methods=['POST'])
def sales_summary():
    try:
        logger.info("Generando resumen de ventas")
        data = request.get_json()
        sender = data.get('sender')
        memory = get_memory(sender)
        idioma = MultiIdioma(memory.global_memory.language)

        ventas_dia_actual = consulta_ventas_dia_actual(sender)
        if ventas_dia_actual is None:
            send_whatsapp_message(
                sender,
                idioma.obtener("MENSAJE_SIN_VENTAS")
            )
            # send_whatsapp_message(sender, "Hoy no se han registrado ventas, recuerda que puedes registrar ventas en el menú de ventas")
        else:
            send_whatsapp_message(
                sender, 
                idioma.obtener("MENSAJE_RESUMEN_VENTAS_FINAL_DIA").format(
                    venta_total=str(ventas_dia_actual.venta_total),
                    unidades_vendidas=str(ventas_dia_actual.unidades_vendidas),
                    num_ventas=str(ventas_dia_actual.num_ventas)
                )
            )

        send_whatsapp_template(sender, idioma.obtener("MENU_INICIO_RAPIDO"))
    except Exception as e:
        logger.error(f"Error al generar resumen de ventas: {e}")
        send_whatsapp_message(sender, idioma.obtener("MENSAJE_ERROR_RESUMEN_VENTAS_FINAL_DIA"))

    return make_response(jsonify({
        'status': 'success',
        'message': 'Resumen de ventas ejecutado correctamente'
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

        memory = get_memory(sender)
        if memory is None:
            return make_response(jsonify({'status': 'error', 'message': 'Error al obtener la memoria'}), 500)

        # Gestión de tareas de inactividad
        if memory.task_name:
            delete_inactivity_task(memory.task_name, sender)
        
        idioma = MultiIdioma(memory.global_memory.language)
        active_state = memory.local_state.get_active_state()

        # --- NUEVA LÓGICA DESACOPLADA ---

        # 1. Recuperar el contenido (mensaje o imagen) acumulado en el estado actual
        image = None
        full_message = None

        if active_state:
            state_obj = getattr(memory.local_state, active_state)
            if hasattr(state_obj, 'is_image') and state_obj.is_image():
                image = state_obj.get_image_content()
            else:
                full_message = state_obj.get_full_user_message()


        logger.info(f"2.1. Contenido recuperado: {full_message}, {image}")
        # 2. Ejecutar el Orquestador
        # El orquestador ahora reemplaza las llamadas manuales a Etapa1 o MenuMachine
        orchestrator = WorkflowOrchestrator(memory)
        orchestrator.process(message=full_message, image=image)

        # Actualizamos la referencia de memoria tras el proceo
        memory = orchestrator.memory

        # --- FIN DE LA LÓGICA DESACOPLADA ---

        # Persistencia y tareas post-procesamiento
        StateMachineExecutor.persist_memory(memory)
        schedule_sales_summary_task(sender)

        if creditos_casi_agotados(memory) or creditos_agotados(memory):
            send_whatsapp_template(sender, idioma.obtener("MENSAJE_CREDITOS_AGOTADOS"))
    
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
        media_url = ''

        # Inicia modificación para procesar imagenes
        try:
            media_url = form_data.get('MediaUrl0', '')
        except:
            pass
        # Termina modificación para procesar imagenes

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

        # confirm = insert_message(sender, receiver, body, data)
        confirm = insert_message(message)
        if confirm is None or not confirm:
            return make_response(jsonify({
                'status': 'error',
                'message': 'Error al insertar el mensaje en la base de datos'
            }), 500)

        # Obtener o crear memoria del usuario
        memory = get_memory(sender)
        if memory is None:
            # Crear nueva memoria para usuario nuevo
            memory = Memory(
                user_id=sender, 
                active_context="Etapa1", 
                machine_stack=[], 
                global_memory=GlobalMemory(), 
                local_state=LocalState(
                    etapa1=GenericResult(
                        active=True,
                        user_message=[body]
                    ), 
                    # etapa2=GenericResult(active=False), 
                    # etapa3=GenericResult(active=False), 
                    # etapa4=GenericResult(active=False)
                ), 
                last_interaction=datetime.now(),
                task_name="")
            # language = language_analyzer(body)
            language = "es"
            memory.global_memory.language = language
            insert_memory(memory)
            # etapa1 = Etapa1(sender, memory.global_memory.datos_negocio, body)
        else:
            # Actualizar memoria existente con el nuevo mensaje
            memory = StateMachineExecutor.process_user_message(memory, body if not media_url else media_url)
            memory.last_interaction = datetime.now()
            StateMachineExecutor.persist_memory(memory)

        if memory.task_name != "":
            delete_inactivity_task(task_name=memory.task_name)

        # Programar tarea de inactividad
        task_id = schedule_inactivity_task(sender)
        memory.task_name = task_id
        StateMachineExecutor.persist_memory(memory)
        
        logger.info("Finalizando ejecución")
    except Exception as e:
        logger.error(f"Error al recibir el mensaje: {e}")
        send_whatsapp_message(sender, "Lo siento, hubo un error al recibir el mensaje")

    return make_response(jsonify({
        'status': 'success'
    }), 200)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)