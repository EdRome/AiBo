import os
import logging
from data.domains.ventas import CreateSalesAction, QuerySalesAction
from data.domains.recordatorios import CreateRemaindersAction, QueryRemaindersAction
from data.domains.tutorial import Bienvenida
from data.domains.conversacion import Agradecimiento
from langchain_google_genai import ChatGoogleGenerativeAI
from .EventWatcher import Watcher
from .layers.llm import LLMLayer
from config.config import MODEL_GEMINI_FLASH_LATEST, ENTITY_TEMPERATURE, ENTITY_MAX_OUTPUT_TOKENS, ENTITY_THINKING_BUDGET
from core.services.whatsapp import send_transition


logger = logging.getLogger(__name__)

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH_LATEST, 
    temperature=ENTITY_TEMPERATURE,
    max_tokens=ENTITY_MAX_OUTPUT_TOKENS,
    thinking_budget=ENTITY_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

class AiBoDirector:

    def __init__(self):
        self.content = {}
        self.llm_layer = LLMLayer(model_client=model)
        self.watcher = Watcher()
        self.actions = {
            'venta': {
                'registrar_venta': CreateSalesAction(),
                'consultar_venta': QuerySalesAction(),
            },
            'recordatorios': {
                'registrar_recordatorio': CreateRemaindersAction(),
                'consultar_recordatorio': QueryRemaindersAction(),
            },
            'bienvenida': Bienvenida(),
            'agradecimiento': Agradecimiento()
        }
        
    def execute_logic(self, memory, current_date, db_session):
        """
        IF message_type == 'interactive' THEN es un mensaje por botón
        IF message_type == 'text' THEN es mensaje de texto libre

        IF message_type == 'interactive' THEN detecta intención por variable intention
        IF message_type == 'text' THEN detecta intención por LLM

        [Aquí no es necesario pasar por el LLM de planeación porque conoces la intención, conoces la acción (después dem mensaje de transición)]
        IF message_type == 'interactive' THEN tratalo como tutorial (intención -> transición -> acción -> respuesta)
        IF message_type == 'text' THEN tratalo como mundo abierto (intención -> planeación -> acción -> respuesta)
        """

        full_message = memory.get_message()
        intention = memory.get_intention()
        message_type = memory.get_message_type()
        action = None

        # Es una acción rápida del menú
        if message_type == 'interactive' and intention in self.actions:
            memory.active_context = intention # Almacena en la BD el estado que debe activarse
            logger.info(f"Este es un mensaje de transición para determinar el subestado del contexto {memory.active_context}")
            send_transition(db_session, memory.user_id, memory.active_context, "transicion")

        # Es la respuesta a la acción rápida del menú
        elif message_type == 'text' and memory.active_context in self.actions: 
            # Determina el subestado de ejecución
            transicion, mensaje, memory, action = self._single_execution(full_message, memory.active_context, memory, db_session, current_date, message_type)
            send_transition(db_session, memory.user_id, memory.active_context, transicion, **mensaje)
            if not (memory.active_context == 'bienvenida' and transicion in ["transicion","transicion_proactiva","pide_nuevamente","mision_ok"]):
                send_transition(db_session, memory.user_id, "IDLE", None)
                memory.reset_active_context()

        elif message_type in ('text','audio') and intention == "":
            logger.info(f"Message Type {message_type}")
            # Envia el menú
            action = self._plan_and_execute(full_message, memory, db_session, current_date, message_type)
            send_transition(db_session, memory.user_id, "IDLE", None)
            memory.reset_active_context()

        else:
            logger.warning(f"Intención no implementada o entendida\n{memory.active_context}\n{message_type}\n{intention}")
            send_transition(db_session, memory.user_id, "errores", "generico")

        memory, mensaje, transicion = self.watcher.execute(memory, action)
        if transicion != '':
            send_transition(db_session, memory.user_id, action, transicion, **mensaje)

        return memory

    def _single_execution(self, message, intention, memory, db_session, current_date, message_type):
        logger.info("Ejecutando acción simple")
        if intention == "bienvenida":
            logger.info("Acción bienvenida")
            action = self.actions[intention]
            action_res = action.execute(memory, message, db_session=db_session, current_date=current_date)
        else:
            subintention = self.llm_layer.identify_action(message, intention) # Identifica el tipo de action que va a ejecutar
            
            action = self.actions[intention][subintention]
            action_res = action.execute(memory, message, db_session=db_session, current_date=current_date)

        memory = action_res.get('memory', memory)
        mensaje = action_res.get('mensaje', {})
        transicion = action_res.get('transicion', '')
        action = action_res.get('action')

        return transicion, mensaje, memory, action

    def _plan_and_execute(self, message, memory, db_session, current_date, message_type):
        execution_plan = self.llm_layer.split_tasks(message, message_type)
        actions = []

        for task in execution_plan:
            if task['action'] == 'menu':
                break
            else:
                context, action_name = task['action'].split(".")
                phrase = task['phrase']
                
                action = self.actions[context][action_name]
                action_res = action.execute(memory, phrase, db_session=db_session, current_date=current_date)
                memory = action_res.get('memory', memory)
                mensaje = action_res.get('mensaje', {})
                transicion = action_res.get('transicion', '')
                action = action_res.get('action')

                send_transition(db_session, memory.user_id, context, transicion, **mensaje)

                memory.reset_active_context()
            
                actions.append(action)

        return actions


