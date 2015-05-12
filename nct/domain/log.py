from nct.domain.base import Base
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.sql import func


class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True) # auto incrementing
    timestamp   = Column(DateTime, default=func.now())
    level       = Column( String(12))
    logger      = Column( String(50) )
    message     = Column( Text)
    trace       = Column( Text)

