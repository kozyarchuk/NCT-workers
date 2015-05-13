from nct.deploy.deploy import Deployer
from nct.utils.alch import Session
from sqlalchemy.engine import create_engine

class TestSchema:
    created = False
    @classmethod
    def create(cls):
        if not cls.created:
            engine = create_engine('sqlite:///:memory:')
            Session.configure( bind=engine)
            Deployer.deploy()
            cls.created = True