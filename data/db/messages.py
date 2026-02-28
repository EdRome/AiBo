import logging
import json
import sqlalchemy
from data.db.utils import get_pool

logger = logging.getLogger(__name__)

def insert_message(sender: str, receiver: str, body: str, data: dict):
    logger.info("Insertando mensaje")
    """
    Inserta un mensaje en la base de datos.
    """
    pool = get_pool()
    json_data_str = json.dumps(data)
    insert_stmt = sqlalchemy.text("INSERT INTO transactional.whatsapp (sender, receiver, body, data) VALUES (:sender, :receiver, :body, :data)")
    with pool.connect() as conn:
        conn.execute(
            insert_stmt, 
            {
                "sender": sender, 
                "receiver": receiver, 
                "body": body, 
                "data": json_data_str
            }
        )
        conn.commit()
        return True