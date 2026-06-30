import os
import logging
import requests
import urllib
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from .repository import get_credentials, update_refresh_token, insert_new_credential

logger = logging.getLogger(__name__)

base_url = os.environ.get('CLOUD_TASK_BASE_URL', '')
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_ID_SECRET = os.environ.get("GOOGLE_CLIENT_ID_SECRET")

def setup_credentials(user_id: str, db_session=None):
    credentials = get_credentials(user_id, db_session)
    
    try:
        if credentials:
            logger.info("# 2. Reconstruyes las credenciales")
            creds = Credentials.from_authorized_user_info(credentials.google_token_data)

            if creds and creds.expired and creds.refresh_token:
                logger.info("Si el access_token expiró (duran 1 hora), usamos el refresh_token de forma transparente")
                creds.refresh(Request())

                logger.info("Actualizas el nuevo token en Supabase para no tener que refrescar en la próxima petición")
                update_refresh_token(user_id, creds.to_json(), db_session=db_session)

            logger.info("4. Instancias el cliente de Calendar (ya autenticado)")
            return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        logger.error(f"Error en el setup de las credenciales {e}")
    return None

def generate_auth_url(user_id: str) -> str:
    """Genera la URL de autenticación para pedir al usuario sus credenciales
    """
    # Configura el flujo con las credenciales de tu cliente OAuth
    redirect_uri = base_url + "/oauth2callback"
    scopes = "https://www.googleapis.com/auth/calendar"
    
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scopes,
        "access_type": "offline",
        "prompt": "select_account consent",
        "state": user_id,  # Tu ID de WhatsApp,
        "include_granted_scopes": "true"

    }

    url_base = "https://accounts.google.com/o/oauth2/auth"
    authorization_url = f"{url_base}?{urllib.parse.urlencode(params)}"
    
    return authorization_url

def oauth_callback(code, user_id, current_date, db_session=None):
    """Cuando el usuario se autentica, Google regresa al callback para construir el token 
    y refresh token de acceso
    """
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
        
        expires_in = token_data.get("expires_in")
        tokens_expires = (current_date + timedelta(seconds=expires_in)).strftime("%Y-%m-%dT%H:%M:%S")

        credentials_json = {
            "token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_ID_SECRET,
            "scopes": ["https://www.googleapis.com/auth/calendar"],
            "expiry": tokens_expires
            # Falta agregar cuando caduda el refresh_token y poder actualizarlo de forma automática
        }
        
        user = get_credentials(user_id, db_session)
        if user:
            update_refresh_token(user_id, credentials_json, db_session)
        else:
            insert_new_credential(user_id, credentials_json, db_session)
        
        return "Cuenta vinculada"
    except Exception as e:
        logger.error(f"Error al vincular la cuenta {e}")
        return None
    
def leer_eventos(user_id: str, fecha_inicio: datetime, fecha_fin: datetime, db_session=None):
    try:
        service = setup_credentials(user_id, db_session)
        if service:
            eventos_resultados = service.events().list(
                calendarId="primary",
                timeMin=fecha_inicio.isoformat(),
                timeMax=fecha_fin.isoformat() if fecha_fin else None,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            eventos = eventos_resultados.get('items', [])
            return eventos

        return None
    except Exception as e:
        logger.error(f"Error al leer los eventos {e}")

def crear_evento_calendario(user_id: str, titulo: str, fecha_inicio: datetime, fecha_fin: datetime, descripcion: str = "", db_session=None):
    """
    Las fechas deben venir en formato ISO 8601, por ejemplo: '2026-06-29T16:00:00-06:00'
    """
    try:
        service = setup_credentials(user_id, db_session)
        
        fecha_fin = fecha_fin + timedelta(hours=1)
        # Estructura requerida por Google Calendar API v3
        evento_body = {
            'summary': titulo,
            'description': descripcion,
            'start': {
                'dateTime': fecha_inicio.isoformat(),
                'timeZone': 'America/Mexico_City', # Ajusta a la zona horaria por defecto o del usuario
            },
            'end': {
                'dateTime': fecha_fin.isoformat(),
                'timeZone': 'America/Mexico_City',
            },
            # Opcional: Puedes añadir recordatorios por correo o notificaciones emergentes
            'reminders': {
                'useDefault': True
            }
        }
        
        if service:
            # Insertar el evento en el calendario principal
            evento_creado = service.events().insert(
                calendarId='primary', 
                body=evento_body
            ).execute()
            
            link_evento = evento_creado.get('htmlLink')
            
            # Respuesta amigable para confirmar al usuario en WhatsApp
            return link_evento

        return None

    except Exception as e:
        logger.error(f"Error al crear el evento: {e}")