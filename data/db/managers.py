import os
import logging
import sqlalchemy
from sqlalchemy.orm import Session, sessionmaker
from google.cloud.sql.connector import Connector, IPTypes

logger = logging.getLogger(__name__)

INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")

connector = Connector()

class DatabaseConnectionManager:

    def __init__(self):
        logger.info("Inicializando gestor de conexiones a la base de datos")
        self.pool = None
        self.session = None
        self.create_pool()
        self.create_session()

    def create_pool(self):
        logger.info("Creando pool de conexiones a la base de datos")
        self.pool = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator =lambda: connector.connect(
                INSTANCE_CONNECTION_NAME,
                "pg8000",
                user=DB_USER,
                password=DB_PASS,
                db=DB_NAME,
                ip_type=IPTypes.PUBLIC
            )
        )

    def create_session(self):
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.pool)
        self.session = SessionLocal()
