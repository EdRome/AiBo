import logging
from typing import List
from pydantic import BaseModel
from unidecode import unidecode
from config.prompts import INSTRUCCION_IDIOMA, CONTEXTO_ASISTENTE

logger = logging.getLogger(__name__)

EXTRAER_INTENCION_PROMPT = """Debes extraer la intención del mensaje del usuario.
La intención puede ser 'registrar_venta','consultar_venta','registrar_recordatorio','consultar_recordatorio' o 'menu'. 
Por defecto, la intención es 'menu'.
Regresa solamente la intención y nada más. Este es el mensaje {mensaje}"""

ROUTER_PROMPT = """
Eres el procesador lógico. Tu misión es desglosar el mensaje del usuario en acciones técnicas ejecutables.

REGLAS DE ORO:
1. MULTI-ACCIÓN: Si el usuario pide varias cosas (ej: "registra venta y ponme un recordatorio"), extrae TODAS las acciones en una lista.
2. EXTRACCIÓN DE DATOS: Identifica la acción y extrae el mensaje correspondiente a la acción.
3. ESTADO POR DEFECTO: Si el mensaje es una charla trivial o no detectas una acción clara, usa 'charla_narrativa'.

ACCIONES DISPONIBLES:
- VENTAS: 'venta.registrar_venta' (los requisitos mínimos son monto y artículo, puede incluir fecha y forma de pago), 'venta.consultar_venta' (requiere la consulta del usuario).
- RECORDATORIOS: 'recordatorios.registrar_recordatorio' (requiere el mensaje del recordatorio y la fecha), 'recordatorios.consultar_recordatorio' (requiere la consulta del usuario).
- MENU: 'menu' (solo si no es posible inferir la acción que quiere hacer el usuario)

REGLAS DE PRIORIZACIÓN:
- La prioridad 1 siempre debe ser el registro de ventas o recordatorios
- La prioridad 2 siempre debe ser la consulta de ventas o recordatorios

MENSAJE DEL USUARIO: {mensaje}
"""

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
            unidecoded_message = unidecode(message).strip().lower()
            if unidecoded_message == 'menu' or unidecoded_message == 'hola':
                return [TaskFragment(action="menu")]
            
            # El LLM devuelve directamente un objeto Pydantic
            task_planer = self.model.with_structured_output(ExecutionPlan)
            plan = task_planer.invoke(prompt)
            
            # Convertimos a lista de diccionarios para el AiBoDirector
            action_plan = [task.model_dump() for task in plan.tasks]
            return self._organiza_plan(action_plan)
            
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
        
    def _organiza_plan(self, action_plan):
        """Organiza el plan de acción, esto particulamente para cubrir un caso donde los recordatorios se confirman
        en distintos mensajes. Esto ocurre con este caso:
        - Mañana sacar a los perros 7am, mañana ir al super 10am
        La explicación es que repetir "mañana" después de cada coma confunde al LLM y produce esa salida no deseada
        """

        try:
            # Separar el plan de acción por tipo
            # Solamente se valida la acción que se tiene identificada con la alucinación
            crear_recordatorios = list(filter(lambda task: task["action"] == "recordatorios.registrar_recordatorio", action_plan))
            consultar_recordatorios = filter(lambda task: task["action"] == "recordatorios.consultar_recordatorio", action_plan)
            crear_venta = filter(lambda task: task["action"] == "venta.registrar_venta", action_plan)
            consultar_venta = filter(lambda task: task["action"] == "venta.consultar_venta", action_plan)

            # SOLO PARA CREAR RECORDATORIOS: Itera la lista y crea una única acción para crear recordatorio con todos los recordatorios.
            # El manejo de la separación se delega al action create_remainders.
            # Esta acción solo se ejecuta si la lista de acción es mayor a 1, cuando el LLM alucina.
            if len(crear_recordatorios) > 1:
                action = ""
                phrase = ""
                for recordatorio in crear_recordatorios:
                    action = recordatorio["action"]
                    phrase += recordatorio["phrase"]+"\n"

                crear_recordatorios = [TaskFragment(action=action, phrase=phrase.strip(), priority=1).model_dump()]

                return crear_recordatorios+list(crear_venta)+list(consultar_recordatorios)+list(consultar_venta)
            else:
                return action_plan
        except Exception as e:
            logger.error(f"Error al organizar el plan {e}")
            return action_plan