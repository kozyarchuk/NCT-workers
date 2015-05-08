from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
import os

mysql_params = dict(host=os.environ['MYSQL_HOST'],
                    user=os.environ['MYSQL_DBO'], 
                    passwd=os.environ['MYSQL_PWD'], 
                    db='NCTData')

engine =  create_engine( "mysql://{user}:{passwd}@{host}/{db}".format(**mysql_params))
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()