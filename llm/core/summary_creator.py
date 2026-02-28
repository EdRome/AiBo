import os
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import MODEL_GEMINI_FLASH, ENTITY_TEMPERATURE, ENTITY_MAX_OUTPUT_TOKENS, ENTITY_THINKING_BUDGET
from data.models.etapa1.negocio import Summary
from llm.prompt.summary_creator import SUMMARY_CREATION_PROMPT
from data.models.etapa3.pain_point import  AffectionSummaryExtractor
from data.models.etapa4.pain_point_summary import PainPointSummary
from llm.prompt.summary_creator import PAIN_POINT_SUMMARY_CREATION_PROMPT, AFFECTION_SUMMARY_PROMPT
from llm.prompt.utils import INSTRUCCION_IDIOMA

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH, 
    temperature=ENTITY_TEMPERATURE,
    max_tokens=ENTITY_MAX_OUTPUT_TOKENS,
    thinking_budget=ENTITY_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

def create_summary(mensaje: str) -> Summary:
    summary_creator = model.with_structured_output(Summary)
    response = summary_creator.invoke(
        INSTRUCCION_IDIOMA + 
        SUMMARY_CREATION_PROMPT.format(mensaje=mensaje)
    )
    return response

def create_pain_point_summary(mensaje: str) -> PainPointSummary:
    pain_point_summary_creator = model.with_structured_output(PainPointSummary)
    response = pain_point_summary_creator.invoke(
        INSTRUCCION_IDIOMA + 
        PAIN_POINT_SUMMARY_CREATION_PROMPT.format(mensaje=mensaje)
    )
    return response

def create_affection_summary(mensaje: str) -> AffectionSummaryExtractor:
    affection_summary_creator = model.with_structured_output(AffectionSummaryExtractor)
    response = affection_summary_creator.invoke(
        INSTRUCCION_IDIOMA + 
        AFFECTION_SUMMARY_PROMPT.format(mensaje=mensaje)
    )
    return response