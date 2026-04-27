import logging
from data.models.memory.memory import Memory, GlobalMemory, LocalState
from data.models.memory.sql_memory import Memory as MemorySQL
from data.db.utils import get_session
from sqlalchemy import update

logger = logging.getLogger(__name__)
db = get_session()


def insert_memory(memory: Memory) -> str:
    logger.info("Insertando memoria")
    """
    Inserta una memoria en la base de datos.
    """

    new_memory = MemorySQL(
        user_id=memory.user_id,
        active_context=memory.active_context,
        machine_stack=memory.machine_stack,
        global_memory=memory.global_memory.model_dump(),
        local_state=memory.local_state.model_dump(),
        last_interaction=memory.last_interaction,
        task_name=memory.task_name,
        creditos_disponibles=memory.creditos_disponibles
    )
    try:
        db.add(new_memory)
        db.commit()
        db.refresh(new_memory)
        return new_memory.user_id
    except Exception as e:
        logger.error(f"Error al insertar la memoria {e}")
        db.rollback()
        return None

def get_memory(user_id: str) -> Memory:
    logger.info("Obteniendo memoria")
    """
    Obtiene una memoria de la base de datos.
    """
    try:
        memory_sql = db.query(MemorySQL).where(MemorySQL.user_id == user_id).first()
        return Memory(
            user_id=memory_sql.user_id,
            active_context=memory_sql.active_context,
            machine_stack=memory_sql.machine_stack,
            global_memory=GlobalMemory(**memory_sql.global_memory),
            local_state=LocalState(**memory_sql.local_state),
            last_interaction=memory_sql.last_interaction,
            task_name=memory_sql.task_name,
            creditos_disponibles=memory_sql.creditos_disponibles
        )
    except Exception as e:
        logger.error(f"Error al obtener la memoria {e}")
        db.rollback()
        return None

def update_memory(memory: Memory) -> bool:
    """
    Actualiza una memoria en la base de datos.
    """
    
    try:
        stmt = update(
            MemorySQL
        ).where(
            MemorySQL.user_id == memory.user_id
        ).values(
            active_context=memory.active_context,
            machine_stack=memory.machine_stack,
            global_memory=memory.global_memory.model_dump(),
            local_state=memory.local_state.model_dump(),
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