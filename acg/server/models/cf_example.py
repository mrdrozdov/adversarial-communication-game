import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import relationship

from .meta import Base


class CFExample(Base):
    __tablename__ = "cf_examples"
    id = Column(Integer, primary_key=True)
    created_at = Column(DATETIME(fsp=6), default=datetime.datetime.now)

    cf_example_set_id = Column(ForeignKey("cf_example_sets.id"), nullable=False)
    cf_example_set = relationship("CFExampleSet", backref="cf_examples")

    example_id = Column(ForeignKey("examples.id"), nullable=False)
    example = relationship("Example", backref="cf_examples")

    label_1_id = Column(ForeignKey("labels.id"), nullable=False)
    label_2_id = Column(ForeignKey("labels.id"), nullable=False)
    label_3_id = Column(ForeignKey("labels.id"), nullable=False)
    label_1 = relationship("Label", foreign_keys=[label_1_id])
    label_2 = relationship("Label", foreign_keys=[label_2_id])
    label_3 = relationship("Label", foreign_keys=[label_3_id])
