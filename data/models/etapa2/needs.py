from pydantic import BaseModel, Field
from typing import List
from data.models.etapa3.pain_point import PainPointAnalysis

class NeedsAnalysis(BaseModel):
    necesidades: List[str] = Field(strict=True, default=[], validate_default=True)
    summary: str = Field(strict=True, default="", validate_default=True)
    punto_de_dolor: str = Field(strict=True, default="", validate_default=True)
    es_respuesta_vaga: bool = Field(strict=True, default=False, validate_default=True)
    frase_vaga: str = Field(strict=True, default="", validate_default=True)
    pain_point: PainPointAnalysis = Field(strict=True, default=PainPointAnalysis(), validate_default=True)

class NeedAnalysisExtraction(BaseModel):
    necesidades: List[str] = Field(strict=True, default=[], validate_default=True)
    summary: str = Field(strict=True, default="", validate_default=True)
    punto_de_dolor: str = Field(strict=True, default="", validate_default=True)
    es_respuesta_vaga: bool = Field(strict=True, default=False, validate_default=True)
    frase_vaga: str = Field(strict=True, default="", validate_default=True)