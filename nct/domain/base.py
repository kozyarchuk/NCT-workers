from sqlalchemy.ext.declarative import declarative_base

class NotFound(Exception): pass
    
Base = declarative_base()
