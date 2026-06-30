import os
import logging
from core.services.google import generate_auth_url, get_credentials

class Watcher:

    def execute(self, memory, action):
        recordatorio = False
        return_obj = {}
        # Valida que la acción sea recordatorio
        if isinstance(action, list):
            # En caso de ser una lista, valida en toda la lista si hubo algún recordatorio
            recordatorio = any([a == 'recordatorios' for a in action])
        else:
            recordatorio = action == 'recordatorios'
        
        if recordatorio:
            return_obj = self.valida_credenciales_google(memory)

        return return_obj.get('memory', memory), return_obj.get('mensaje', {}), return_obj.get('transicion', '')

    def valida_credenciales_google(self, memory):
        return_obj = {}
        # Si el usuario no se ha registrado, envía mensaje con opción para registrarse
        if not memory.request_google_calendar:
            auth_url = generate_auth_url(memory.user_id)
            return_obj['mensaje'] = {'auth_url': auth_url}
            return_obj['transicion'] = "conectar_calendario"
            return_obj['memory'] = memory
            memory.request_google_calendar = True