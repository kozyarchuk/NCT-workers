from nct.domain.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from nct.domain.choicelist import ChoiceList

class Entity(Base):
    __tablename__ = 'entity'

    id          = Column( Integer, primary_key=True)
    name        = Column( String(255), unique = True)
    description = Column( String(255))
    type_id     = Column( Integer, ForeignKey('choice_list.id')) 
    type        = relationship("ChoiceList")

    @classmethod
    def find(cls, s, type_name, name):
        type_ = ChoiceList.find(s, 'EntityType', type_name)
        return s.query(cls).filter_by(name=name, type=type_).one()

