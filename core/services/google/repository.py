import logging
from .models import UserCredentials
from data.config.database import get_session
from sqlalchemy import update

logger = logging.getLogger(__name__)

def get_credentials(user_id: str, db_session=None):
    logger.info("Obteniendo credenciales")
    try:
        db = db_session or get_session()
        user_credentials = db.query(
            UserCredentials
        ).where(
            UserCredentials.user_id == user_id
        ).first()
        return user_credentials
    except Exception as e:
        logger.error(f"Error al obtener las credenciales {e}")
        return None
    
def update_refresh_token(user_id: str, google_token_data: dict, db_session=None):
    logger.info("Actualizando refresh token")
    db = db_session or get_session()
    try:
        stmt = update(
            UserCredentials
        ).where(
            UserCredentials.user_id == user_id
        ).values(
            google_token_data = google_token_data
        )

        db.execute(stmt)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error al actualizar el refresh token {e}")
        db.rollback()
        return False

def insert_new_credential(user_id: str, google_token_data: dict, db_session=None):
    new_credential = UserCredentials(
        user_id=user_id,
        google_token_data=google_token_data
    )

    db = db_session or get_session()
    
    try:
        db.add(new_credential)
        db.commit()
    except Exception as e:
        logger.error(f"Error al insertar la credencial {e}")
        db.rollback()