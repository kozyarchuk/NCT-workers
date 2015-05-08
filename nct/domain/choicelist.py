from nct.domain.base import Base
from sqlalchemy import Column, Integer, String

class ChoiceList(Base):
    __tablename__ = 'choice_list'

    id          = Column( Integer, primary_key=True)
    list_name   = Column( String(255))
    value       = Column( String(255))
    
    @classmethod
    def find_by_name(cls,s, list_name, value):
        return s.query(ChoiceList).filter_by(list_name = list_name, value = value).one()
