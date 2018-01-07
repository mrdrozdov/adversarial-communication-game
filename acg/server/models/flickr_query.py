import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import relationship

from .meta import Base


class FlickrQuery(Base):
    __tablename__ = "flickr_queries"
    id = Column(Integer, primary_key=True)
    created_at = Column(DATETIME(fsp=6), default=datetime.datetime.now)
    query = Column(String(300))
    page = Column(Integer())
    per_page = Column(Integer())
    total = Column(Integer())

    flickr_query_set_id = Column(ForeignKey("flickr_query_sets.id"), nullable=True)
    flickr_query_set = relationship("FlickrQuerySet", backref="flickr_queries")
