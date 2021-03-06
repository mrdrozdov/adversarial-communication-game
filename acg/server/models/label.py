from sqlalchemy import (
    Column,
    String,
    Integer)

from .meta import Base


class Label(Base):
    __tablename__ = 'labels'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
