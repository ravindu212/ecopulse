from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings


if settings.environment == "production":
    # Serverless instances are short-lived and scale independently. Let Neon's
    # pooled endpoint manage connection reuse instead of retaining a pool in
    # every Vercel function instance.
    engine = create_engine(settings.database_url, poolclass=NullPool)
else:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Provide a short-lived database session for FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
