import os
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import MODEL_GEMINI_FLASH, ENTITY_TEMPERATURE, ENTITY_MAX_OUTPUT_TOKENS, ENTITY_THINKING_BUDGET
from data.models.gastos.RegistroGasto import GastoCreate, Gasto
from llm.prompt.expenses_extractor import EXPENSES_EXTRACTOR_PROMPT
from llm.prompt.utils import INSTRUCCION_IDIOMA

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH, 
    temperature=ENTITY_TEMPERATURE,
    max_tokens=ENTITY_MAX_OUTPUT_TOKENS,
    thinking_budget=ENTITY_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

def get_expenses_data(mensaje: str, phone_number: str) -> Gasto:
    expenses_extractor = model.with_structured_output(GastoCreate)
    gasto_create = expenses_extractor.invoke(
        INSTRUCCION_IDIOMA + 
        EXPENSES_EXTRACTOR_PROMPT.format(mensaje=mensaje)
    )
    gasto = parse_gasto(gasto_create, phone_number)
    return gasto

def parse_gasto(gasto_create: GastoCreate, phone_number: str) -> Gasto:
    gasto_create_dump = gasto_create.model_dump()

    dump_model = {}
    dump_model['detalles'] = gasto_create_dump['detalles']
    # Por salud, valida que las cantidades no sean 0
    for detalle in dump_model['detalles']:
        if detalle['cantidad'] == 0:
            detalle['cantidad'] = 1
    # También crea el método de pago si no viene vacío
    if gasto_create_dump['metodo_pago'] != '':
        dump_model['metodo_pago'] = gasto_create_dump['metodo_pago']

    dump_model['phone_number'] = phone_number
    gasto = Gasto(**dump_model)
    # De una vez calcula el total
    gasto.calcula_total()
    return gasto