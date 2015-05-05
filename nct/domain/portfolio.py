from nct.domain.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey


class Portfolio(Base):
    __tablename__ = 'portfolio'

    id          = Column( Integer, primary_key=True)
    description = Column( String(255))
    trader_id   = Column( Integer, ForeignKey('entity.id'))
    analyst_id  = Column( Integer, ForeignKey('entity.id'))
    broker_id   = Column( Integer, ForeignKey('entity.id'))
    clearer_id  = Column( Integer, ForeignKey('entity.id'))
    category_1  = Column( String(255))
    category_2  = Column( String(255))
    category_3  = Column( String(255))



