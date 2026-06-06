import os
import logging
import sqlalchemy
from contextlib import contextmanager
from sqlalchemy.orm import Session, sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from google.cloud.sql.connector import Connector, IPTypes

logger = logging.getLogger(__name__)

INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")

environment = os.environ.get("ENVIRONMENT", "supabase")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT", "")
DB_HOST = os.environ.get("DB_HOST", "")


connector = Connector()

class DatabaseConnectionManager:

    def __init__(self):
        logger.info("Inicializando gestor de conexiones a la base de datos")
        self.pool = None
        self.session = None
        self.environ = environment
        self.create_pool()
        self.create_session()

    def create_pool(self):
        logger.info("Creando pool de conexiones a la base de datos")
        if self.environ == 'supabase':
            self.pool = sqlalchemy.create_engine(
                f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
                poolclass=NullPool
            )
        else:
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

# _db_manager = DatabaseConnectionManager()
engine = sqlalchemy.create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

session_factory = sessionmaker(bind=engine)

db_session = scoped_session(session_factory)

@contextmanager
def get_db():
    db = db_session
    try:
        yield db
    except:
        db_session.remove()

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