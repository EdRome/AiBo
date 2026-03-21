import os
from unidecode import unidecode
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import MODEL_GEMINI_FLASH, ENTITY_TEMPERATURE, ENTITY_MAX_OUTPUT_TOKENS, ENTITY_THINKING_BUDGET
from llm.prompt.entity_extractor import DATOS_NEGOCIO_EXTRACTION_PROMPT, EXTRAER_INTENCION_PROMPT
from data.models.etapa1.negocio import EntityExtractor
from llm.prompt.utils import INSTRUCCION_IDIOMA, CONTEXTO_ASISTENTE

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH, 
    temperature=ENTITY_TEMPERATURE,
    max_tokens=ENTITY_MAX_OUTPUT_TOKENS,
    thinking_budget=ENTITY_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

def confirm_delete(mensaje: str) -> bool:
    unidecoded_message = unidecode(mensaje).strip().lower()
    return unidecoded_message == 'si'

def extract_business_and_name(message: str) -> EntityExtractor:
    """Extrae el nombre de negocio y nombre del emprendedor"""
    name_business_extractor = model.with_structured_output(EntityExtractor)
    response = name_business_extractor.invoke(
        CONTEXTO_ASISTENTE +
        INSTRUCCION_IDIOMA + 
        DATOS_NEGOCIO_EXTRACTION_PROMPT.format(mensaje=message)
    )
    return response

def get_intention(message: str) -> str:
    """Obtiene la intención del usuario"""
    unidecoded_message = unidecode(message).strip().lower()
    if unidecoded_message in ['registrar venta','nueva venta']:
        return 'registrar_venta'
    if unidecoded_message in ['borrar venta','borrar ventas','borra venta','borra ventas']:
        return 'borrar_venta'
    elif unidecoded_message in ['registrar inventario','nueva inventario']:
        return 'registrar_inventario'
    elif unidecoded_message in ['borrar inventario','borra inventario','borrar inventarios','borra inventarios']:
        return 'borrar_inventario'
    elif unidecoded_message in ['otras acciones']:
        return 'otras_acciones'
    elif unidecoded_message in ['menu']:
        return 'menu'
    else:
        return model.invoke(
            INSTRUCCION_IDIOMA + 
            EXTRAER_INTENCION_PROMPT.format(mensaje=unidecoded_message)
        ).content