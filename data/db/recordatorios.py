import logging
import json
import sqlalchemy
from data.db.utils import get_pool
from data.db.utils import get_session
from data.models.sqlalchemy.recordatorios import Recordatorio

logger = logging.getLogger(__name__)

db = get_session()

def insert_recordatorio(recordatorio: Recordatorio):
    try:
        db.add(recordatorio)
        db.commit()
        logger.info(f"Recordatorio insertado: {recordatorio}")
        return recordatorio
    except Exception as e:
        db.rollback()
        logger.error(f"Error al insertar recordatorio: {e}")
        return None

def get_last_recordatorio(recordatorio: Recordatorio):
    try:
        return db.query(
            Recordatorio
        ).filter(
            Recordatorio.user_id == recordatorio.user_id,
            Recordatorio.estatus == "activo"
        ).order_by(
            Recordatorio.fecha_creacion.desc()
        ).first()
    except Exception as e:
        logger.error(f"Error al obtener recordatorio: {e}")
        return None

def get_recordatorio_by_id(recordatorio: Recordatorio):
    try:
        return db.query(
            Recordatorio
        ).filter(
            Recordatorio.id == recordatorio.id
        ).first()
    except Exception as e:
        logger.error(f"Error al obtener recordatorio: {e}")
        return None

def get_recordatorio_by_date(recordatorio: Recordatorio):
    try:
        return db.query(
            Recordatorio
        ).filter(
            Recordatorio.fecha_recordatorio == recordatorio.fecha_recordatorio,
            Recordatorio.estatus == "activo",
            Recordatorio.user_id == recordatorio.user_id
        ).order_by(
            Recordatorio.fecha_creacion.desc()
        )
    except Exception as e:
        logger.error(f"Error al obtener recordatorio: {e}")
        return None

def get_recordatorio_by_fonetica(recordatorio: Recordatorio):
    pass

def get_recordatorio_by_keywords(recordatorio: Recordatorio):
    pass

def update_recordatorio(recordatorio: Recordatorio):
    try:
        recordatorio_actualizado = db.query(
            Recordatorio
        ).filter(
            Recordatorio.id == recordatorio.id
        ).first()
        if recordatorio_actualizado:
            recordatorio_actualizado.titulo = recordatorio.titulo
            recordatorio_actualizado.descripcion = recordatorio.descripcion
            recordatorio_actualizado.estatus = recordatorio.estatus
            recordatorio_actualizado.fecha_recordatorio = recordatorio.fecha_recordatorio
            recordatorio_actualizado.fecha_actualizacion = recordatorio.fecha_actualizacion
            recordatorio_actualizado.keywords = recordatorio.keywords
            db.add(recordatorio_actualizado)
            db.commit()
            logger.info(f"Recordatorio actualizado: {recordatorio}")
        else:
            logger.error(f"Recordatorio no encontrado: {recordatorio}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar recordatorio: {e}")

def delete_recordatorio(recordatorio: Recordatorio):
    try:
        recordatorio_actualizado = db.query(
            Recordatorio
        ).filter(
            Recordatorio.id == recordatorio.id
        ).first()
        if recordatorio_actualizado:
            recordatorio_actualizado.estatus = "borrado"
            db.add(recordatorio_actualizado)
            db.commit()
            logger.info(f"Recordatorio eliminado: {recordatorio}")
        else:
            logger.error(f"Recordatorio no encontrado: {recordatorio}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar recordatorio: {e}")
