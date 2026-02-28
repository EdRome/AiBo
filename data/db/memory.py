import json
import logging
from datetime import datetime
import sqlalchemy
from typing import List
from data.db.utils import get_pool
from data.models.memory.memory import Memory

logger = logging.getLogger(__name__)

def insert_memory(memory: Memory) -> int:
    logger.info("Insertando memoria")
    """
    Inserta una memoria en la base de datos.
    """
    pool = get_pool()
    json_global_memory_str = memory.global_memory.model_dump_json()
    json_local_state_str = memory.local_state.model_dump_json()
    last_interaction_str = memory.last_interaction.isoformat()
    insert_stmt = sqlalchemy.text("INSERT INTO transactional.memory (user_id, active_context, machine_stack, global_memory, local_state, last_interaction, creditos_disponibles) VALUES (:user_id, :active_context, :machine_stack, :global_memory, :local_state, :last_interaction, :creditos_disponibles)")
    with pool.connect() as conn:
        conn.execute(
            insert_stmt, 
            {
                "user_id": memory.user_id, 
                "active_context": memory.active_context, 
                "machine_stack": memory.machine_stack, 
                "global_memory": json_global_memory_str, 
                "local_state": json_local_state_str, 
                "last_interaction": last_interaction_str,
                "creditos_disponibles": 20
            }
        )
        conn.commit()
        return True

def get_memory(user_id: str) -> Memory:
    logger.info("Obteniendo memoria")
    """
    Obtiene una memoria de la base de datos.
    """
    pool = get_pool()
    select_stmt = sqlalchemy.text("SELECT * FROM transactional.memory WHERE user_id = :user_id")
    with pool.connect() as conn:
        result = conn.execute(
            select_stmt, 
            {"user_id": user_id}
        )
        row = result.fetchone()
        if row is None:
            return None
        # Convertir row a diccionario
        row_dict = dict(row._mapping)
        # Parsear campos JSON
        row_dict["global_memory"] = row_dict["global_memory"]
        row_dict["local_state"] = row_dict["local_state"]
        # Parsear last_interaction desde ISO8601 string a datetime
        row_dict["last_interaction"] = row_dict["last_interaction"]
        row_dict["task_name"] = row_dict["task_name"] if row_dict["task_name"] else ""
        row_dict["creditos_disponibles"] = row_dict["creditos_disponibles"] if row_dict["creditos_disponibles"] else 20
        return Memory(**row_dict)

def update_memory(user_id: str, active_context: str, machine_stack: List[str], 
                    global_memory: dict, local_state: dict, last_interaction: datetime, 
                    task_name: str, creditos_disponibles: int) -> bool:
    """
    Actualiza una memoria en la base de datos.
    """
    pool = get_pool()
    json_global_memory_str = json.dumps(global_memory)
    json_local_state_str = json.dumps(local_state)
    last_interaction_str = last_interaction.isoformat()
    update_stmt = sqlalchemy.text("UPDATE transactional.memory SET active_context = :active_context, machine_stack = :machine_stack, global_memory = :global_memory, local_state = :local_state, last_interaction = :last_interaction, task_name = :task_name, creditos_disponibles = :creditos_disponibles WHERE user_id = :user_id")
    with pool.connect() as conn:
        conn.execute(
            update_stmt, 
            {
                "active_context": active_context, 
                "machine_stack": machine_stack, 
                "global_memory": json_global_memory_str, 
                "local_state": json_local_state_str, 
                "last_interaction": last_interaction_str, 
                "user_id": user_id,
                "task_name": task_name,
                "creditos_disponibles": creditos_disponibles
            }
        )
        conn.commit()
        return True