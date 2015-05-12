from nct.domain.base import Base, NotFound
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

class Instrument(Base):
    __tablename__ = 'instrument'

    id          = Column( Integer, primary_key=True)
    name        = Column( String(255), nullable = False, unique = True)
    currency_id = Column( Integer, ForeignKey('instrument.id'))
    ins_type_id = Column( Integer, ForeignKey('choice_list.id'), nullable = False) 
    underlying_id = Column( Integer, ForeignKey('instrument.id')) 
    exp_date    = Column( Date) 
    
    ins_type    = relationship("ChoiceList")
    currency    = relationship("Instrument", remote_side=[id], foreign_keys="[Instrument.currency_id]", post_update=True)
    underlying  = relationship("Instrument",remote_side=[id], foreign_keys="[Instrument.underlying_id]")

    @classmethod
    def find(cls, s, name):
        try:
            return s.query(cls).filter_by(name=name).one()
        except NoResultFound:
            raise NotFound(">{}< Not Found".format(name))

