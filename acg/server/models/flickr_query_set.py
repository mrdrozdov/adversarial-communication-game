
from sqlalchemy import (
    Column,
    Integer)

from .meta import Base


class FlickrQuerySet(Base):
    __tablename__ = "flickr_query_sets"
    id = Column(Integer, primary_key=True)
