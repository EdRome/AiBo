import os
import logging
from twilio.rest import Client
from data.db.messages import insert_message

logger = logging.getLogger(__name__)

client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))

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

def send_whatsapp_message(to, body):
    try:
        logger.info(f"Enviando mensaje a {to} con body {body}")
        message = client.messages.create(
            from_='whatsapp:' + os.environ.get("TWILIO_WHATSAPP_NUMBER"),
            to='whatsapp:' + to,
            body=body
        )
        insert_message(os.environ.get("TWILIO_WHATSAPP_NUMBER"), to, body, {})
        return message
    except Exception as e:
        logger.error(f"Error al enviar el mensaje: {e}")
        return None