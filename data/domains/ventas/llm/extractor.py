import os
import base64
from unidecode import unidecode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from ..schemas import VentaCreate, Venta, BatchVentas, SalesQueryExtraction
from .prompts import SALES_EXTRACTOR_PROMPT, EXTRAER_IMAGEN_DATOS_VENTA, QUERY_SALES_PROMPT
from config.prompts import INSTRUCCION_IDIOMA, CONTEXTO_ASISTENTE
from config.utils import calcular_rango_fechas
from config.llm import MODEL_GEMINI_FLASH, ENTITY_TEMPERATURE, ENTITY_MAX_OUTPUT_TOKENS, ENTITY_THINKING_BUDGET

semana_referencia_map = {
    "actual": 0,
    "pasada": 1
}

rango_map = {
    "hoy": 0,
    "ayer": 1,
    "esta_semana": 7,
    "semana_pasada": 14,
    "este_mes": 30,
    "mes_pasado": 60
}

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH, 
    temperature=ENTITY_TEMPERATURE,
    max_tokens=ENTITY_MAX_OUTPUT_TOKENS,
    thinking_budget=ENTITY_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

def get_sales_data(mensaje: str, phone_number: str, current_date) -> Venta:
    sales_extractor = model.with_structured_output(VentaCreate)
    venta_create = sales_extractor.invoke(
        INSTRUCCION_IDIOMA + 
        CONTEXTO_ASISTENTE.format(current_date=current_date.strftime("%Y-%m-%d %H:%M")) +
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

def get_image_content(image_data: bytes, current_date):
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    ocr = model.with_structured_output(BatchVentas)

    prompt_texto = INSTRUCCION_IDIOMA + \
    CONTEXTO_ASISTENTE.format(current_date=current_date.strftime("%Y-%m-%d %H:%M")) + \
    EXTRAER_IMAGEN_DATOS_VENTA
    
    mensaje = HumanMessage(
        content=[
            {"type": "text", "text": prompt_texto},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            },
        ]
    )

    response = ocr.invoke([mensaje])
    return response

def confirm_delete(mensaje: str) -> bool:
    unidecoded_message = unidecode(mensaje).strip().lower()
    return unidecoded_message == 'si'

def get_sales_query(mensaje:str, current_date):
    sales_query = model.with_structured_output(SalesQueryExtraction)
    res = sales_query.invoke(
        INSTRUCCION_IDIOMA +
        CONTEXTO_ASISTENTE.format(current_date=current_date.strftime("%Y-%m-%d %H:%M")) +
        QUERY_SALES_PROMPT.format(mensaje=mensaje)
    )

    start_date, end_date = calcular_rango_fechas(res.rango_solicitado, current_date, res)

    
    venta_query = {
        "start_date": start_date.in_timezone("UTC").date(),
        "end_date": end_date.in_timezone("UTC").date(),
        "group_by": res.group_by
    }

    return venta_query