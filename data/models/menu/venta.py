import os
import requests
from requests.auth import HTTPBasicAuth
from pydantic import BaseModel, Field
from typing import Optional, List
from urllib.parse import urlparse

class Venta(BaseModel):
    # Campos de estado de la máquina
    active: bool = Field(default=False)
    step: str = Field(default="waiting_product")
    product: Optional[str] = None
    quantity: Optional[int] = None
    
    # Historial de mensajes (para compatibilidad con executor genérico)
    user_message: List[str] = Field(default_factory=list)
    aibo_message: List[str] = Field(default_factory=list)
    
    borrar_venta: bool = Field(default=False)
    procesar_venta: bool = Field(default=False)

    id_ultima_venta: int = Field(default=0)

    def is_image(self):
        for message in self.user_message:
            parsed_url = urlparse(message)
            if parsed_url.scheme and parsed_url.netloc:
                return True
        return False

    def get_content(self):
        if self.is_image():
            return self.get_image_content()
        else:
            return self.get_full_user_message()

    def get_full_user_message(self):
        return "\n".join(self.user_message)

    def get_image_content(self):
        for message in self.user_message:
            parsed_url = urlparse(message)
            if parsed_url.scheme and parsed_url.netloc:
                basic = HTTPBasicAuth(
                    os.environ.get("TWILIO_ACCOUNT_SID"), 
                    os.environ.get("TWILIO_AUTH_TOKEN")
                )
                image_data = requests.get(message, auth=basic).content
                return image_data
        return None
