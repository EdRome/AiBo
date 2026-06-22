import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import timedelta
from zoneinfo import ZoneInfo
from ..schemas import Recordatorio, ListaRecordatorios, RemainderQueryExtraction
from .prompts import REMAINDER_EXTRACTOR_PROMPT, QUERY_REMAINDERS_PROMPT
from config.prompts import INSTRUCCION_IDIOMA, CONTEXTO_ASISTENTE
from config.utils import calcular_rango_fechas
from config.llm import MODEL_GEMINI_FLASH, ENTITY_TEMPERATURE, ENTITY_MAX_OUTPUT_TOKENS, ENTITY_THINKING_BUDGET

logger = logging.getLogger(__name__)
tz_cdmx = ZoneInfo('America/Mexico_City')

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH, 
    temperature=ENTITY_TEMPERATURE,
    max_tokens=ENTITY_MAX_OUTPUT_TOKENS,
    thinking_budget=ENTITY_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

def get_remainder_data(message, user_id, current_date):
    try:
        remainder_extractor = model.with_structured_output(ListaRecordatorios)
        recordatorio_create = remainder_extractor.invoke(
            CONTEXTO_ASISTENTE.format(current_date=current_date.strftime("%Y-%m-%d %H:%M")) +
            INSTRUCCION_IDIOMA + 
            REMAINDER_EXTRACTOR_PROMPT.format(message=message)
        )


        recordatorios_return = []
        for recordatorio in recordatorio_create.recordatorios:
            recordatorio_cdmx = recordatorio.fecha_recordatorio.replace(tzinfo=tz_cdmx)
            if (recordatorio_cdmx - current_date).days < 0:
                recordatorio_cdmx += timedelta(days=1)
            
            recordatorios_return.append(
                Recordatorio(
                    phone_number=user_id, 
                    fecha_recordatorio=recordatorio_cdmx, 
                    recordatorio=recordatorio.recordatorio)
            )

        return recordatorios_return
    except Exception as e:
        logger.error(f"Error al extraer información del recordatorio: {e}")
        return None
    
def get_remainder_query_extractor(message, current_date):
    try:
        query_extractor = model.with_structured_output(RemainderQueryExtraction)
        res = query_extractor.invoke(
            CONTEXTO_ASISTENTE.format(current_date=current_date.strftime("%Y-%m-%d %H:%M")) +
            INSTRUCCION_IDIOMA +
            QUERY_REMAINDERS_PROMPT.format(mensaje=message)
        )

        logger.info("##################### RES #####################")
        logger.info(res)
        logger.info("###############################################")

        start_date, end_date = calcular_rango_fechas(res.rango_solicitado, current_date, res)

        logger.info("##################### RANGO FECHAS #####################")
        logger.info(start_date)
        logger.info(end_date)
        logger.info("########################################################")
        
        remainder_query = {
            "start_date": start_date.date(),
            "end_date": end_date.date(),
            "search_query": res.search_query
        }

        return remainder_query
    except Exception as e:
        logger.error(f"Error al extraer información de la consulta de recordatorio: {e}")
        return None