"""
Database base model for SQLAlchemy entities
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model for all SQLAlchemy entities"""
    __abstract__ = True
