import logging
from datetime import timedelta
from data.config.database import get_session
from .schemas import Memory, GlobalMemory
from .models import Memory as MemorySQL
from .models import MemoriaEstados as MemoriaEstadosSQL
from sqlalchemy import update, func, or_

logger = logging.getLogger(__name__)


def insert_memory(memory: Memory, db_session=None) -> str:
    logger.info("Insertando memoria")
    """
    Inserta una memoria en la base de datos.
    """

    new_memory = MemorySQL(
        user_id=memory.user_id,
        active_context=memory.active_context,
        machine_stack=memory.machine_stack,
        global_memory=memory.global_memory.model_dump(),
        local_state=memory.local_state,
        last_interaction=memory.last_interaction,
        task_name=memory.task_name,
        creditos_disponibles=memory.creditos_disponibles
    )
    db = db_session or get_session()
    try:
        db.add(new_memory)
        db.commit()
        db.refresh(new_memory)
        return new_memory.user_id
    except Exception as e:
        logger.error(f"Error al insertar la memoria {e}")
        db.rollback()
        return None

def get_memory(user_id: str, db_session=None) -> Memory:
    logger.info("Obteniendo memoria")
    """
    Obtiene una memoria de la base de datos.
    """
    db = db_session or get_session()
    try:
        memory_sql = db.query(MemorySQL).where(MemorySQL.user_id == user_id).first()
        if memory_sql:
            return Memory(
                user_id=memory_sql.user_id,
                active_context=memory_sql.active_context,
                machine_stack=memory_sql.machine_stack,
                global_memory=GlobalMemory(**memory_sql.global_memory),
                local_state=memory_sql.local_state,
                last_interaction=memory_sql.last_interaction,
                task_name=memory_sql.task_name,
                creditos_disponibles=memory_sql.creditos_disponibles
            )
        return None
    except Exception as e:
        logger.error(f"Error al obtener la memoria {e}")
        db.rollback()
        return None

def update_memory(memory: Memory, db_session=None) -> bool:
    """
    Actualiza una memoria en la base de datos.
    """
    db = db_session or get_session()
    try:
        stmt = update(
            MemorySQL
        ).where(
            MemorySQL.user_id == memory.user_id
        ).values(
            active_context=memory.active_context,
            machine_stack=memory.machine_stack,
            global_memory=memory.global_memory.model_dump(),
            local_state=memory.local_state,
            last_interaction=memory.last_interaction,
            task_name=memory.task_name,
            creditos_disponibles=memory.creditos_disponibles
        )
        db.execute(stmt)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error al actualizar la memoria {e}")
        db.rollback()
        return False

def get_memory_state(user_id: str, db_session=None):
    db = db_session or get_session()
    try:
        memoria_estado_sql = db.query(MemoriaEstadosSQL).where(MemoriaEstadosSQL.user_id == user_id).first()
        if not memoria_estado_sql:
            return MemoriaEstadosSQL(user_id = user_id)

        return memoria_estado_sql
    except Exception as e:
        logger.error(f"Error al obtener la memoria de estados {e}")
        db.rollback()
        return None

def insert_memory_state(memory_state, db_session=None):
    db = db_session or get_session()
    try:
        db.add(memory_state)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error al insertar el memory_state {e}")
        db.rollback()
        return False
    
def get_2_more_days_last_interaction(current_date, db_session=None):
    db = db_session or get_session()
    hace_dos_dias = current_date - timedelta(days=2)
    hace_siete_dias = current_date - timedelta(days=7)
    try:
        memories = db.query(
            MemorySQL
        ).where(
            func.timezone("America/Mexico_City", MemorySQL.last_interaction) <= hace_dos_dias,
            func.timezone("America/Mexico_City", MemorySQL.last_interaction) >= hace_siete_dias
        ).all()

        return [Memory(
                user_id=memory.user_id,
                active_context=memory.active_context,
                machine_stack=memory.machine_stack,
                global_memory=GlobalMemory(**memory.global_memory),
                local_state=memory.local_state,
                last_interaction=memory.last_interaction,
                task_name=memory.task_name,
                creditos_disponibles=memory.creditos_disponibles
        ) for memory in memories]
    except Exception as e:
        logger.error(f"Error al consultar usuarios con 2 o más días de inactividad")
        db.rollback()
        return None