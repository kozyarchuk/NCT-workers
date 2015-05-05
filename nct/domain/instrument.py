from nct.domain.base import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey

class Instrument(Base):
    __tablename__ = 'instrument'

    id          = Column( Integer, primary_key=True)
    name        = Column( String(255))
    currency_id = Column( Integer, ForeignKey('instrument.id'))
    ins_type    = Column( Integer, ForeignKey('choice_list.id')) 
    underlying_id = Column( Integer, ForeignKey('instrument.id')) 
    exp_date    = Column( Date) 

