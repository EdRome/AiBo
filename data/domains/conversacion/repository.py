import logging
from data.config.database import get_session
from config.utils import pick_random_text
from .models import MensajesDescrube

logger = logging.getLogger(__name__)

def consultar_mensaje_by_funcionalidad(funcionalidad, db_session=None) -> MensajesDescrube:
    db = db_session or get_session()

    mensaje = db.query(
        MensajesDescrube
    ).filter(
        MensajesDescrube.funcionalidad == funcionalidad
    ).first()

    return mensaje

def get_mensaje_random(db_session=None) -> MensajesDescrube:
    db = db_session or get_session()
    ids = db.query(
        MensajesDescrube.id
    ).all()

    random_id = pick_random_text(ids)

    mensaje = db.query(
        MensajesDescrube
    ).filter(
        MensajesDescrube.id == random_id
    ).first()

    return mensaje
