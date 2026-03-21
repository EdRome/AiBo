import os
import requests
from pydantic import BaseModel, Field
from typing import Optional, List

class Etapa1(BaseModel):
    active: bool = Field(default=False)
    step: str = Field(default="onboarding")
    
    user_message: List[str] = Field(default_factory=list)
    aibo_message: List[str] = Field(default_factory=list)

    def get_full_user_message(self):
        return "\n".join(self.user_message)