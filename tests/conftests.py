# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Importas la clase Base de tus modelos de SQLAlchemy (o de tu config)
from data.config.database import Base 

@pytest.fixture(scope="function")
def db_session():
    """Crea una base de datos SQLite temporal en memoria para cada prueba."""
    # Creamos un motor temporal en memoria
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    
    # Creamos todas las tablas reflejadas en tus modelos de SQLAlchemy
    Base.metadata.create_all(bind=engine)
    
    # Creamos la fábrica de sesiones de prueba
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session  # Le entregamos la sesión limpia a la prueba
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)  # Destruimos todo al terminar