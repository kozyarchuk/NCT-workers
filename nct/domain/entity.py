from nct.domain.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class Entity(Base):
    __tablename__ = 'entity'

    id          = Column( Integer, primary_key=True)
    name        = Column( String(255))
    description = Column( String(255))
    type        = Column( Integer, ForeignKey('choice_list.id')) 

