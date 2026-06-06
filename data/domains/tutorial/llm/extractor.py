import os
from unidecode import unidecode
from langchain_google_genai import ChatGoogleGenerativeAI
from ..schemas import Onboarding
from .prompts import ONBOARDING_EXTRACTOR_PROMPT
from config.prompts import INSTRUCCION_IDIOMA, CONTEXTO_ASISTENTE
from config.llm import MODEL_GEMINI_FLASH, ENTITY_TEMPERATURE, ENTITY_MAX_OUTPUT_TOKENS, ENTITY_THINKING_BUDGET

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH, 
    temperature=ENTITY_TEMPERATURE,
    max_tokens=ENTITY_MAX_OUTPUT_TOKENS,
    thinking_budget=ENTITY_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

def get_onboarding_data(mensaje: str, current_date) -> Onboarding:
    unidecoded_message = unidecode(mensaje).lower()

    if unidecoded_message == 'hola':
        return Onboarding()

    onboarding_extractor = model.with_structured_output(Onboarding)
    onboarding_data = onboarding_extractor.invoke(
        INSTRUCCION_IDIOMA +
        CONTEXTO_ASISTENTE.format(current_date=current_date.strftime("%Y-%m-%d %H:%M")) +
        ONBOARDING_EXTRACTOR_PROMPT.format(mensaje=mensaje)
    )
    return onboarding_data