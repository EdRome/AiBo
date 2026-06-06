import os
import logging
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import MODEL_GEMINI_FLASH, ENTITY_TEMPERATURE, ENTITY_MAX_OUTPUT_TOKENS, ENTITY_THINKING_BUDGET
from data.models.recordatorio.RegistroRecordatorio import Recordatorio, ListaRecordatorios
from llm.prompt.remainder_extractor import REMAINDER_EXTRACTOR_PROMPT
from llm.prompt.utils import INSTRUCCION_IDIOMA, CONTEXTO_ASISTENTE
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)
tz_cdmx = ZoneInfo('America/Mexico_City')

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH, 
    temperature=ENTITY_TEMPERATURE,
    max_tokens=ENTITY_MAX_OUTPUT_TOKENS,
    thinking_budget=ENTITY_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

def get_remainder_data(message, user_id):
    try:
        remainder_extractor = model.with_structured_output(ListaRecordatorios)
        recordatorio_create = remainder_extractor.invoke(
            CONTEXTO_ASISTENTE +
            INSTRUCCION_IDIOMA + 
            REMAINDER_EXTRACTOR_PROMPT.format(message=message)
        )
        
        logger.info(recordatorio_create.recordatorios)

        return [
            Recordatorio(
                phone_number=user_id,
                fecha_recordatorio=recordatorio.fecha_recordatorio.replace(tzinfo=tz_cdmx),
                recordatorio=recordatorio.recordatorio
            ) for recordatorio in recordatorio_create.recordatorios
        ]
    except Exception as e:
        logger.error(f"Error al extraer información del recordatorio: {e}")
        return None