from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# When you later run migrations,
# SQLAlchemy looks at everything that inherits from Base and knows exactly what tables to create in PostgreSQL.
# Without Base — SQLAlchemy has no idea your class is a DB table. It's just a regular Python class.
# Think of it as registration — Base is the registry, every model signs up by inheriting from it.
