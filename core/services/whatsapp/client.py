import os
import json
import logging
from twilio.rest import Client
from data.domains.mensajes import insert_message, Message
from data.db.s3.s3_conn import get_s3_storage

logger = logging.getLogger(__name__)

_sticker_cache = {}
client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
storage = get_s3_storage()
sender = os.environ.get("TWILIO_WHATSAPP_NUMBER")

def _persist(to, body, is_image=False, db_session=None):
    insert_message(
        Message(
            sender=sender,
            receiver=to,
            body=body if not is_image else "",
            data={},
            multimedia=body if is_image else ""
        ),
        db_session
    )

def get_sticker(sticker_name):
    if sticker_name in _sticker_cache:
        return _sticker_cache[sticker_name]
    
    response = storage.create_signed_url(path="aibo/"+sticker_name, expires_in=3600)

    # Extraemos la URL específica
    if isinstance(response, dict) and "signedURL" in response:
        signed_url = response["signedURL"]
    else:
        signed_url = response

    _sticker_cache[sticker_name] = signed_url
    return signed_url

def send_whatsapp_template(to, content_sid, content_variables=None):
    try:
        logger.info(f"Enviando mensaje a {to} con content_sid {content_sid} y content_variables {content_variables}")
        if content_variables is None:
            _ = client.messages.create(
                from_='whatsapp:' + os.environ.get("TWILIO_WHATSAPP_NUMBER"),
                to='whatsapp:' + to,
                content_sid=content_sid
            )
        else:
            _ = client.messages.create(
                from_='whatsapp:' + os.environ.get("TWILIO_WHATSAPP_NUMBER"),
                to='whatsapp:' + to,
                content_sid=content_sid,
                content_variables=json.dumps(content_variables)
            )
        _persist(to, content_sid)
        return content_sid
    except Exception as e:
        logger.error(f"Error al enviar el mensaje: {e}")
        return None

def send_whatsapp_message(to, body, is_image=False, db_session=None):
    try:
        logger.info(f"Enviando mensaje a {to} con body {body}")
        if is_image:
            url = get_sticker(body)
            body = url
            
        message = client.messages.create(
            from_='whatsapp:' + sender,
            to='whatsapp:' + to,
            body=body if not is_image else None,
            media_url=body if is_image else None
        )
        _persist(to, body, is_image, db_session)
        return message
    except Exception as e:
        logger.error(f"Error al enviar el mensaje: {e}")
        return None