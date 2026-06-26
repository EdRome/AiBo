import os
import logging
import requests
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from .repository import get_credentials, update_refresh_token

logger = logging.getLogger(__name__)

base_url = os.environ.get('CLOUD_TASK_BASE_URL', '')
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_ID_SECRET = os.environ.get("GOOGLE_CLIENT_ID_SECRET")

def setup_credentials(user_id: str, db_session=None):
    credentials = get_credentials(user_id, db_session)
    
    # 2. Reconstruyes las credenciales
    creds = Credentials.from_authorized_user_info(credentials.google_token_data.data[0]['token_data'])

    # 3. El paso más importante para optimizar Cloud Run:
    if creds and creds.expired and creds.refresh_token:
        # Si el access_token expiró (duran 1 hora), usamos el refresh_token de forma transparente
        creds.refresh(Request())

        # Actualizas el nuevo token en Supabase para no tener que refrescar en la próxima petición
        update_refresh_token(user_id, creds.to_json())

    # 4. Instancias el cliente de Calendar (ya autenticado)
    return build('calendar', 'v3', credentials=creds)

def generate_auth_url(user_id: str) -> str:
    # Configura el flujo con las credenciales de tu cliente OAuth
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_ID_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    
    # Tu URL de callback registrada en la consola de Google Cloud
    flow.redirect_uri = base_url + "/oauth2callback"
    
    # Generamos la URL pasando el user_id en el 'state'
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account consent', # Fuerza a pedir permisos y mostrar el refresh token
        state=user_id # <-- CRUCIAL: Vincula el flujo con el usuario de WhatsApp
    )
    
    return authorization_url

def oauth_callback(code, user_id):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_ID_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": base_url + "/oauth2callback" 
    }
    
    try:
        response = requests.post(token_url, data=payload)
        token_data = response.json()
        
        if "error" in token_data:
            raise Exception(json.dumps(token_data))
        
        credentials_json = {
            "token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_ID_SECRET,
            "scopes": ["https://www.googleapis.com/auth/calendar"]
        }
        
        update_refresh_token(user_id, json.dumps(credentials_json))
        
        return "Cuenta vinculada"
    except Exception as e:
        logger.error(f"Error al vincular la cuenta {e}")
        return None