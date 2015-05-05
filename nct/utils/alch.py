from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine
import os
from nct.domain import Base


mysql_params = dict(host=os.environ['MYSQL_HOST'],
                    user=os.environ['MYSQL_DBO'], 
                    passwd=os.environ['MYSQL_PWD'], 
                    db='NCTData')

def get_engine():
    return create_engine( "mysql://{user}:{passwd}@{host}/{db}".format(**mysql_params))

_Session = None
def get_session():
    global _Session
    _Session = sessionmaker(bind=get_engine())
    return _Session()


def build_schema():
    engine = get_engine( )
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    