from pydantic import BaseModel, Field
from typing import List

class PainPointAnalysis(BaseModel):
    afectacion: str = Field(strict=True, default="", validate_default=True)
    tiempo: bool = Field(strict=True, default=False, validate_default=True)
    incertidumbre: bool = Field(strict=True, default=False, validate_default=True)
    dinero: bool = Field(strict=True, default=False, validate_default=True)
    causa_raiz: str = Field(strict=True, default="", validate_default=True)
    objetivo_general: str = Field(strict=True, default="", validate_default=True)
    resumen_punto_de_dolor: str = Field(strict=True, default="", validate_default=True)
    otros: List[str] = Field(strict=True, default=[], validate_default=True)

class AffectionAnalysisExtractor(BaseModel):
    tiempo: bool = Field(strict=True, default=False, validate_default=True)
    incertidumbre: bool = Field(strict=True, default=False, validate_default=True)
    dinero: bool = Field(strict=True, default=False, validate_default=True)

class AffectionSummaryExtractor(BaseModel):
    afectacion: str = Field(strict=True, default="", validate_default=True)