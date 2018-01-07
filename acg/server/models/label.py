from sqlalchemy import (
    Column,
    String,
)

from .meta import Base


class Label(Base):
    __tablename__ = 'labels'
    name = Column(String(64), primary_key=True)
