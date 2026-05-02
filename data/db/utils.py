import logging
from data.db.managers import DatabaseConnectionManager
# from data.db.managers.cloud_sql import DatabaseConnectionManager
# from data.db.managers.supabase import DatabaseConnectionManager

logger = logging.getLogger(__name__)

_db_manager = DatabaseConnectionManager()

def get_pool():
    """
    Función de conveniencia para obtener un pool de conexiones a la DB.
    Usa el gestor singleton de conexiones.
    """
    return _db_manager.pool

def get_session():
    """
    Función de conveniencia para obtener sesiones de conexión a la DB.
    Usa el gestor singleton de conexiones.
    """
    return _db_manager.session