from datetime import datetime
from nct.domain import Log
from nct.utils.alch import session_scope
from logging import Handler
import traceback

class DBLogger(Handler):

    def emit(self, record ):
            
        trace = traceback.format_exc(record.exc_info) if record.exc_info else None
                
        with session_scope() as s:
            s.add( Log(timestamp = datetime.now(), level = record.levelname, 
                logger = record.name, trace = trace, message = record.msg) )

    