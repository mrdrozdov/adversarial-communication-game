
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey)
from sqlalchemy.orm import relationship

from .meta import Base


class ExampleFile(Base):
    __tablename__ = "example_files"
    id = Column(Integer, primary_key=True)
    img_path = Column(String(300))
    desc_path = Column(String(300))
    example_id = Column(ForeignKey("examples.id"), nullable=False)
    example = relationship("Example", backref="file")

