from nct.domain.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import event
import hashlib


class Portfolio(Base):
    __tablename__ = 'portfolio'

    id          = Column( Integer, primary_key=True)
    description = Column( String(255))
    trader_id   = Column( Integer, ForeignKey('entity.id'))
    analyst_id  = Column( Integer, ForeignKey('entity.id'))
    broker_id   = Column( Integer, ForeignKey('entity.id'))
    clearer_id  = Column( Integer, ForeignKey('entity.id'))
    fund_id     = Column( Integer, ForeignKey('entity.id'))
    strategy    = Column( String(255))
    sector      = Column( String(255))
    hash_value  = Column( String(255), nullable = False, unique = True)

    trader  = relationship("Entity",foreign_keys="[Portfolio.trader_id]")
    broker  = relationship("Entity",foreign_keys="[Portfolio.broker_id]")
    analyst = relationship("Entity",foreign_keys="[Portfolio.analyst_id]")
    clearer = relationship("Entity",foreign_keys="[Portfolio.clearer_id]")
    fund    = relationship("Entity",foreign_keys="[Portfolio.fund_id]")

    @classmethod
    def find_by_hash(cls, s, hash_value):
        return s.query(cls).filter_by(hash_value = hash_value).first()
    
    def hash_function(self):
        def formatter( col_name):
            if col_name.endswith("_id"):
                value = getattr(self,col_name.replace("_id",""))
                return repr(value.id) if value else repr(value)
            else:
                return repr(getattr(self,col_name))
        return "<{}({})>".format(
            self.__class__.__name__,
            ', '.join(
                ["{}={}".format(k, formatter(k))
                    for k in sorted(c.name for c in self.__table__.columns)
                    if k != 'hash_value']
            )
        )
        
    def get_hash_value(self):
        return "{}:{}".format(self.__class__.__name__, 
                      hashlib.sha224(self.hash_function().encode('utf-8')).hexdigest())


def populate_hash_value(mapper, connection, target):
    target.hash_value  = target.get_hash_value()

event.listen(Portfolio, 'before_insert', populate_hash_value)

