"""Database models and session management for SCDO"""
import os
import logging
from typing import Optional, Generator
from contextlib import contextmanager

logger = logging.getLogger(__name__)

try:
    from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.pool import QueuePool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logger.warning("sqlalchemy not installed — database features disabled")

if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()

    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/scdo")

    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False,
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    class SyllabusModel(Base):
        __tablename__ = "syllabi"

        id = Column(String(36), primary_key=True)
        course_title = Column(String(255), nullable=False)
        course_code = Column(String(50), nullable=False)
        credits = Column(String(20))
        data = Column(JSON)
        created_at = Column(DateTime)
        updated_at = Column(DateTime)

    class AnalysisModel(Base):
        __tablename__ = "analyses"

        id = Column(String(36), primary_key=True)
        syllabus_id = Column(String(36), nullable=False)
        analysis_type = Column(String(50))
        result = Column(JSON)
        created_at = Column(DateTime)

    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def init_db():
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
else:
    def get_db():
        yield None

    def init_db():
        pass
