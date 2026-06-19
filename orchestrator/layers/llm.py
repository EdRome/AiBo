import logging
from typing import List
from pydantic import BaseModel
from unidecode import unidecode
from llm.prompt.entity_extractor import ROUTER_PROMPT, EXTRAER_INTENCION_PROMPT
from llm.prompt.utils import INSTRUCCION_IDIOMA, CONTEXTO_ASISTENTE

from pydantic import BaseModel
from typing import List

logger = logging.getLogger(__name__)

class TaskFragment(BaseModel):
    action: str # Ejemplo: 'registrar_venta', 'registrar_recordatorio', 'consultar_expediente'
    phrase: str # El pedazo de texto original del usuario
    priority: int # Para decidir qué ejecutar primero (opcional)

class ExecutionPlan(BaseModel):
    tasks: List[TaskFragment]

class LLMLayer:
    def __init__(self, model_client):
        self.model = model_client

    def split_tasks(self, message: str) -> List[dict]:
        """
        Divide el mensaje en fragmentos accionables.
        """
        prompt = INSTRUCCION_IDIOMA + CONTEXTO_ASISTENTE + ROUTER_PROMPT.format(mensaje=message)
        
        try:
            # El LLM devuelve directamente un objeto Pydantic
            task_planer = self.model.with_structured_output(ExecutionPlan)
            plan = task_planer.invoke(prompt)
            
            # Convertimos a lista de diccionarios para el AiBoDirector
            logger.info(plan)
            return [task.model_dump() for task in plan.tasks]
            
        except Exception as e:
            print(f"Error en el Router: {e}")
            # Fallback seguro: tratar todo como charla narrativa
            return [{"action": "charla_narrativa", "fragmento": message, "prioridad": 0}]
        
    def identify_action(self, message, intention):
        """Obtiene la intención del usuario"""
        logger.info("Identificando acción")
        unidecoded_message = unidecode(message).strip().lower()

        words_in_message = set(unidecoded_message.split())
        if intention == 'venta':
            keywords_consulta = {'consultar', 'ver', 'dame', 'dar', 'cuales', 'semana', 'mes', 'dia', 'diario', 'cuanto', 'reporte'}
            if words_in_message.intersection(keywords_consulta):
                return 'consultar_venta'
            else:
                return 'registrar_venta'
        elif intention == 'recordatorios':
            keywords_consulta = {'consultar', 'dame', 'dar', 'cuales', 'tengo', 'pendientes', 'recordatorios', 'lista'}
            if words_in_message.intersection(keywords_consulta):
                return 'consultar_recordatorio'
            else:
                return 'registrar_recordatorio'
        elif unidecoded_message in ['hola','menu','ola','.']:
            return 'IDLE'
        else:
            return self.model.invoke(
                INSTRUCCION_IDIOMA + 
                CONTEXTO_ASISTENTE +
                EXTRAER_INTENCION_PROMPT.format(mensaje=unidecoded_message)
            ).content