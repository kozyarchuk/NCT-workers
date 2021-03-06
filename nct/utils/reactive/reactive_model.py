from nct.utils.reactive.bound_field import BoundField
from nct.utils.reactive.field_factory import FieldFactory
from nct.utils.alch import Session

class ReactiveModel:
    INSTRUMENT = 'Instrument'
    TRADE = 'Trade'
    PORTFOLIO = 'Portfolio'
    FIELD_DEPENDS = { }

    @classmethod
    def model_name(cls):
        return str(cls.__name__).replace("Model","")
    
    def __init__(self):
        self.s = Session()
        self._domain_objects = self._init_domain_objects()

    def _init_domain_objects(self):
        return {}
    
    def get_domain_object(self, name):
        return self._domain_objects[ name ]

    def bind_fields(self):
        for field_name in self.FIELD_DEPENDS:
            setattr(self, field_name, BoundField(FieldFactory.get_field(field_name), self))

    def must_be_provided(self, field):
        return None if field.has_value else 'Not set'

    def  _commit(self):
        try:
            self.s.commit()
        except:
            self.s.rollback()
            raise

    def close(self): 
        if self.s:
            self.s.close()
