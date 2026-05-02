import logging
from data.models.recordatorio.RegistroRecordatorio import Recordatorio, RecordatorioBase
from data.models.recordatorio.sql_recordatorio import Recordatorio as RecordatorioSQL
from data.db.utils import get_session
from sqlalchemy import update, func

logger = logging.getLogger(__name__)
db = get_session()

def insert_remainder(recordatorio: RecordatorioBase):
    try:
        new_remainder = RecordatorioSQL(
            phone_number = recordatorio.phone_number,
            task_id = recordatorio.task_id,
            fecha_recordatorio = recordatorio.fecha_recordatorio,
            mensaje = recordatorio.recordatorio,
            time_delta = recordatorio.time_delta,
            status = recordatorio.status
        )
        db.add(new_remainder)
        db.commit()
        return new_remainder.id
    except Exception as e:
        logger.error(f"Error al guardar recordatorio: {e}")
        return None

def update_remainder(recordatorio: RecordatorioBase):
    try:
        stmt = update(
            RecordatorioSQL
        ).where(
            RecordatorioSQL.task_id == recordatorio.task_id
        ).values(
            status = recordatorio.status
        )

        db.execute(stmt)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error al actualizar recordatorio: {e}")
        return None

def get_remainder_count(user_id: str) -> int:
    try:
        count = db.query(
            func.count(RecordatorioSQL.id)
        ).where(
            RecordatorioSQL.phone_number == user_id
        ).scalar()
        return count or 0
    except Exception as e:
        logger.error(f"Error al recuperar todos los recordatorios: {e}")
        return 0