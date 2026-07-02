import os
import logging
from flask import Blueprint, jsonify, request, make_response
from data.config.database import get_db
from core.services.google import oauth_callback
from core.services.whatsapp import send_whatsapp_message
from config.utils import get_current_date

logger = logging.getLogger(__name__)

webhooks_bp = Blueprint('webhooks', __name__)
numero_aibo = os.environ.get("TWILIO_WHATSAPP_NUMBER")

@webhooks_bp.route('/oauth2callback', methods=["GET"])
def oauth2callback():
    code = request.args.get("code")
    user_id = request.args.get("state")
    try:
        if not code or not user_id:
            return make_response(jsonify({
                'status': 'sucess',
                'message': 'Parámetros insuficientes'
            }), 200)

        with get_db() as db:
            message = oauth_callback(code, user_id, get_current_date(), db)
            if message is not None:
                send_whatsapp_message(
                    user_id,
                    message,
                    db_session=db
                )
    except Exception as e:
        logger.error(f"Error durante el callback de oauth {e}")
    finally:
        wa_url = f"https://wa.me/{numero_aibo}"

        html = f"""<!doctype html>
    <html><head><meta charset="utf-8"></head>
    <body>
    <script>
    // Regresa al chat de WhatsApp
    window.location.replace("{wa_url}");

    // Fallback si el webview no permite la navegación
    setTimeout(function() {{
        window.location.replace("/oauth/success?ok=1");
    }}, 1000);
    </script>
    </body></html>"""

        return make_response(html, 200)