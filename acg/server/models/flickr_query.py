import datetime

from sqlalchemy import (
    Column,
    Integer,
    String)
from sqlalchemy.dialects.mysql import DATETIME

from .meta import Base


class FlickrQuery(Base):
    __tablename__ = "flickr_queries"
    id = Column(Integer, primary_key=True)
    created_at = Column(DATETIME(fsp=6), default=datetime.datetime.now)
    query = Column(String(300))

