import logging
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import func
from data.db.utils import get_pool
from data.db.utils import get_session
from data.models.sqlalchemy.messages import Message

logger = logging.getLogger(__name__)
tz_cdmx = ZoneInfo("America/Mexico_City")
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

def check_streak(user_id):
    try:
        date_col = func.date(Message.created_at)
        dates = db.query(
            date_col
        ).where(
            Message.sender == user_id
        ).distinct(

        ).all()

        if not dates: return 0

        dates.sort(reverse=True)

        streak = 0
        today = datetime.now(tz_cdmx).date
        current_check = today

        for date_row in dates:
            if date_row[0] == current_check:
                streak += 1
                current_check -= timedelta(days=1)
            elif date_row[0] > current_check:
                continue
            else:
                break
        return streak
    except Exception as e:
        logger.error(f"Error al consultar racha {e}")