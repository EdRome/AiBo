from pydantic import BaseModel, Field

class PainPointSummary(BaseModel):
    resumen_punto_de_dolor: str = Field(strict=True, default="", validate_default=True)
    causa_raiz: str = Field(strict=True, default="", validate_default=True)
    objetivo_general: str = Field(strict=True, default="", validate_default=True)