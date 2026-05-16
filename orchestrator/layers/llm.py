import os
from typing import List, Optional
from pydantic import BaseModel
from unidecode import unidecode
from langchain_google_genai import ChatGoogleGenerativeAI
from llm.prompt.entity_extractor import ROUTER_PROMPT
from llm.prompt.utils import INSTRUCCION_IDIOMA, CONTEXTO_ASISTENTE

from pydantic import BaseModel
from typing import List

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
            return [task.model_dump() for task in plan.tasks]
            
        except Exception as e:
            print(f"Error en el Router: {e}")
            # Fallback seguro: tratar todo como charla narrativa
            return [{"action": "charla_narrativa", "fragmento": message, "prioridad": 0}]