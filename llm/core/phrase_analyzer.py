import os
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import MODEL_GEMINI_FLASH, ENTITY_TEMPERATURE, ENTITY_MAX_OUTPUT_TOKENS, ENTITY_THINKING_BUDGET
from data.models.etapa1.negocio import DatosNegocio
from data.models.etapa2.needs import NeedAnalysisExtraction
from data.models.etapa2.channels import ChannelAnalysis
from data.models.etapa3.pain_point import PainPointAnalysis
from data.models.etapa3.pain_point import AffectionAnalysisExtractor
from llm.prompt.phrase_analyzer import CHANNEL_ANALYSIS_PROMPT, NEED_ANALYSIS_PROMPT, MAIN_PAIN_ANALYSIS_PROMPT, AFFECTION_ANALYSIS_PROMPT, OTHER_PAIN_ANALYSIS_PROMPT, LANGUAGE_ANALYZER_PROMPT
from llm.prompt.utils import INSTRUCCION_IDIOMA

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH, 
    temperature=ENTITY_TEMPERATURE,
    max_tokens=ENTITY_MAX_OUTPUT_TOKENS,
    thinking_budget=ENTITY_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

def language_analyzer(mensaje: str) -> str:
    if "hi" in mensaje.lower() or "hello" in mensaje.lower() or "name" in mensaje.lower():
        return "en"
    elif "hola" in mensaje.lower() or "nombre" in mensaje.lower():
        return "es"
    else:
        language_analyzer = model.with_structured_output(str)
        response = language_analyzer.invoke(
            LANGUAGE_ANALYZER_PROMPT.format(mensaje=mensaje)
        )
        return response

def need_analyzer(mensaje: str, datos_negocio: DatosNegocio) -> NeedAnalysisExtraction:
    need_analyzer = model.with_structured_output(NeedAnalysisExtraction)
    response = need_analyzer.invoke(NEED_ANALYSIS_PROMPT.format(
        giro=datos_negocio.negocio.giro,
        descripcion=datos_negocio.negocio.descripcion,
        mensaje=mensaje
    ))
    return response

def channel_analyzer(mensaje: str) -> ChannelAnalysis:
    channel_analyzer = model.with_structured_output(ChannelAnalysis)
    response = channel_analyzer.invoke(
        INSTRUCCION_IDIOMA + 
        CHANNEL_ANALYSIS_PROMPT.format(mensaje=mensaje)
    )
    return response

def main_pain_analyzer(mensaje: str) -> PainPointAnalysis:
    pain_point_analyzer = model.with_structured_output(PainPointAnalysis)
    response = pain_point_analyzer.invoke(
        INSTRUCCION_IDIOMA + 
        MAIN_PAIN_ANALYSIS_PROMPT.format(mensaje=mensaje)
    )
    return response

def affection_analyzer(mensaje: str) -> AffectionAnalysisExtractor:
    affection_analyzer = model.with_structured_output(AffectionAnalysisExtractor)
    response = affection_analyzer.invoke(
        INSTRUCCION_IDIOMA + 
        AFFECTION_ANALYSIS_PROMPT.format(mensaje=mensaje)
    )
    return response

def other_pain_analyzer(mensaje: str, principal_punto_de_dolor: str) -> List[str]:
    other_pain_analyzer = model.with_structured_output(List[str])
    response = other_pain_analyzer.invoke(
        INSTRUCCION_IDIOMA + 
        OTHER_PAIN_ANALYSIS_PROMPT.format(mensaje=mensaje, principal_punto_de_dolor=principal_punto_de_dolor)
    )
    return response