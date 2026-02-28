import os
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import MODEL_GEMINI_FLASH, ENTITY_TEMPERATURE, ENTITY_MAX_OUTPUT_TOKENS, ENTITY_THINKING_BUDGET
from data.models.venta.RegistroVenta import VentaCreate, Venta
from llm.prompt.sales_extractor import SALES_EXTRACTOR_PROMPT
from llm.prompt.utils import INSTRUCCION_IDIOMA

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH, 
    temperature=ENTITY_TEMPERATURE,
    max_tokens=ENTITY_MAX_OUTPUT_TOKENS,
    thinking_budget=ENTITY_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

def get_sales_data(mensaje: str, phone_number: str) -> Venta:
    sales_extractor = model.with_structured_output(VentaCreate)
    venta_create = sales_extractor.invoke(
        INSTRUCCION_IDIOMA + 
        SALES_EXTRACTOR_PROMPT.format(mensaje=mensaje)
    )
    venta = parse_venta(venta_create, phone_number)
    return venta

def parse_venta(venta_create: VentaCreate, phone_number: str) -> Venta:
    venta_create_dump = venta_create.model_dump()

    dump_model = {}
    dump_model['detalles'] = venta_create_dump['detalles']
    # Por salud, valida que las cantidades no sean 0
    for detalle in dump_model['detalles']:
        if detalle['cantidad'] == 0:
            detalle['cantidad'] = 1
    # También crea el método de pago si no viene vacío
    if venta_create_dump['metodo_pago'] != '':
        dump_model['metodo_pago'] = venta_create_dump['metodo_pago']

    dump_model['phone_number'] = phone_number
    venta = Venta(**dump_model)
    # De una vez calcula el total
    venta.calcula_total()
    return venta

def get_image_content(image_data: bytes) -> Venta:
    """
    TODO: Hacer que el extractor procese bytes
    """
    sales_extractor = model.with_structured_output(VentaCreate)
    venta_create = sales_extractor.invoke(
        INSTRUCCION_IDIOMA + 
        SALES_IMAGES_EXTRACTOR_PROMPT
    )
    venta = parse_venta(venta_create, phone_number)
    return venta