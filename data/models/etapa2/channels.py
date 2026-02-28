from pydantic import BaseModel, Field
from typing import List

class RedesSociales(BaseModel):
    facebook: bool = Field(strict=True, default=False, validate_default=True)
    instagram: bool = Field(strict=True, default=False, validate_default=True)
    twitter_x: bool = Field(strict=True, default=False, validate_default=True)
    linkedin: bool = Field(strict=True, default=False, validate_default=True)
    youtube: bool = Field(strict=True, default=False, validate_default=True)
    tiktok: bool = Field(strict=True, default=False, validate_default=True)
    twitch: bool = Field(strict=True, default=False, validate_default=True)
    discord: bool = Field(strict=True, default=False, validate_default=True)
    whatsapp: bool = Field(strict=True, default=False, validate_default=True)
    otros: List[str] = Field(strict=True, default=[], validate_default=True)
    principal_canal: str = Field(strict=True, default="", validate_default=True)

class ChannelAnalysis(BaseModel):
    redes_sociales: RedesSociales = Field(strict=True, default=RedesSociales(), validate_default=True)
    boca_boca: bool = Field(strict=True, default=False, validate_default=True)
    sin_canales_claros: bool = Field(strict=True, default=False, validate_default=True)
    descripcion: str = Field(strict=True, default="", validate_default=True)

    def has_multiple_social_networks(self):
        num_sns = sum([val for _, val in self.redes_sociales.model_dump().items() if isinstance(val, bool)])
        return num_sns > 1