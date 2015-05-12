from nct.domain.base import Base, NotFound
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.orm.exc import NoResultFound

class ChoiceList(Base):
    __tablename__ = 'choice_list'

    id          = Column( Integer, primary_key=True)
    list_name   = Column( String(255), nullable = False)
    value       = Column( String(255), nullable = False)
    __table_args__ = (UniqueConstraint('list_name', 'value'),
                     )   
    @classmethod
    def find(cls,s, list_name, value):
        try:
            return s.query(ChoiceList).filter_by(list_name = list_name, value = value).one()
        except NoResultFound:
            raise NotFound(">{}< Not Found".format(value))
