from .client import get_sticker, send_whatsapp_message, send_whatsapp_template
from .translator import get_text_by_lang

def send_translated_message(db_session, user_phone, message_key, is_image=False, lang="es", **kwargs):
    if not is_image:
        text = get_text_by_lang(message_key, lang, **kwargs)
    else:
        text = message_key

    return send_whatsapp_message(user_phone, text, is_image, db_session)

def send_transition(db_session, user_phone, active_context, message_key, **kwargs):
    text = get_text_by_lang(active_context, message_key=message_key, **kwargs)
    if active_context == 'IDLE' and message_key != 'menu_tutorial':
        return send_whatsapp_template(user_phone, text, kwargs)
    elif active_context == 'recordatorios' and message_key == 'conectar_calendario':
        return send_whatsapp_template(user_phone, text, kwargs)
    return send_whatsapp_message(user_phone, text, False, db_session)

__all__ = [
    "get_sticker",
    "send_whatsapp_message",
    "send_whatsapp_template",
    "get_text_by_lang",
    "send_translated_message",
    "send_transition"
]