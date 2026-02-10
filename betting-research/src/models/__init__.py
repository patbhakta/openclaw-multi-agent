"""
SQLAlchemy ORM Models

Database models using SQLAlchemy ORM for type-safe database access.
All models include account_id for row-level security.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base

# Base class for all models
Base = declarative_base()

# Import all models
from .user import User
from .api_key import APIKey
from .paper_trade import PaperTrade
from .security_event import SecurityEvent
from .api_call_log import APICallLog

# Export all models
__all__ = [
    'Base',
    'User',
    'APIKey',
    'PaperTrade',
    'SecurityEvent',
    'APICallLog',
]


def create_tables(engine):
    """
    Create all tables in the database

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)
