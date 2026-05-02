import os
import logging
from twilio.rest import Client
from data.db.messages import insert_message
from data.models.sqlalchemy.messages import Message
from data.db.s3.s3_conn import get_s3_storage

logger = logging.getLogger(__name__)

client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
storage = get_s3_storage()

def get_sticker(sticker_name):
    response = storage.create_signed_url(path="aibo/"+sticker_name, expires_in=300)

    # Extraemos la URL específica
    if isinstance(response, dict) and "signedURL" in response:
        signed_url = response["signedURL"]
    else:
        signed_url = response

    return signed_url

def send_whatsapp_template(to, content_sid, content_variables=None):
    try:
        logger.info(f"Enviando mensaje a {to} con content_sid {content_sid} y content_variables {content_variables}")
        if content_variables is None:
            message = client.messages.create(
                from_='whatsapp:' + os.environ.get("TWILIO_WHATSAPP_NUMBER"),
                to='whatsapp:' + to,
                content_sid=content_sid
            )
        else:
            message = client.messages.create(
                from_='whatsapp:' + os.environ.get("TWILIO_WHATSAPP_NUMBER"),
                to='whatsapp:' + to,
                content_sid=content_sid,
                content_variables=content_variables
            )
        return message
    except Exception as e:
        logger.error(f"Error al enviar el mensaje: {e}")
        return None

def send_whatsapp_message(to, body, is_image=False):
    try:
        logger.info(f"Enviando mensaje a {to} con body {body}")
        if is_image:
            url = get_sticker(body)
            message = client.messages.create(
                from_='whatsapp:' + os.environ.get("TWILIO_WHATSAPP_NUMBER"),
                to='whatsapp:' + to,
                media_url=url
            )

            insert_message(
                Message(
                    sender=os.environ.get("TWILIO_WHATSAPP_NUMBER"),
                    receiver=to,
                    body="",
                    data={},
                    multimedia=url
                )
            )
        else:
            message = client.messages.create(
                from_='whatsapp:' + os.environ.get("TWILIO_WHATSAPP_NUMBER"),
                to='whatsapp:' + to,
                body=body
            )

            insert_message(
                Message(
                    sender=os.environ.get("TWILIO_WHATSAPP_NUMBER"),
                    receiver=to,
                    body=body,
                    data={},
                    multimedia=""
                )
            )
        # insert_message(os.environ.get("TWILIO_WHATSAPP_NUMBER"), to, body, {})
        return message
    except Exception as e:
        logger.error(f"Error al enviar el mensaje: {e}")
        return None