import datetime
import uuid

from sqlalchemy import (
    ForeignKey,
    Float,
    String,
    Integer)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import TypeDecorator, CHAR

from .meta import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    source: http://docs.sqlalchemy.org/en/rel_0_9/core/custom_types.html?highlight=guid#backend-agnostic-guid-type

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class Example(Base):
    __tablename__ = 'examples'
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    resource_id = Column(String(64))
    created_at = Column(DATETIME(fsp=6), default=datetime.datetime.now)

    label_id = Column(ForeignKey("labels.id"), nullable=True)
    flickr_query_id = Column(ForeignKey("flickr_queries.id"), nullable=True)

    rank = Column(Integer())
    url_m = Column(String(128))
    url_s = Column(String(128))
    url_z = Column(String(128))
    width_m = Column(Float())
    width_s = Column(Float())
    width_z = Column(Float())
    height_m = Column(Float())
    height_s = Column(Float())
    height_z = Column(Float())
    flickr_data = Column(String(4096))

    label = relationship("Label", backref="examples")
    flickr_query = relationship("FlickrQuery", backref="results")
