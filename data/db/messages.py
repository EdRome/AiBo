import logging
import json
import sqlalchemy
from data.db.utils import get_pool
from data.db.utils import get_session
from data.models.sqlalchemy.messages import Message

logger = logging.getLogger(__name__)

db = get_session()

def insert_message(message: Message):
    try:
        db.add(message)
        db.commit()
        db.refresh(message)
        return message.id
    except Exception as e:
        db.rollback()
        logger.error(f"Error al insertar el mensaje {e}")
        return None