from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import get_settings

# Crea la conexión a Postgres y la Session por request de la applicación.

settings = get_settings()

engine = create_engine(settings.DB_POSTGRESQL_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_session() -> Session:
    db = SessionLocal()
    try:
        yield db          # el endpoint / use-case trabaja aquí
        db.commit()       # si todo salió bien
    except Exception:
        db.rollback()     # ante cualquier error
        raise
    finally:
        db.close()
