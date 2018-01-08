import datetime

from sqlalchemy import (
    Column,
    Integer)
from sqlalchemy.dialects.mysql import DATETIME

from .meta import Base


class CFExampleSet(Base):
    __tablename__ = "cf_example_sets"
    id = Column(Integer, primary_key=True)
    created_at = Column(DATETIME(fsp=6), default=datetime.datetime.now)
