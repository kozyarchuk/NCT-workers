from nct.utils.reactive.bound_field import BoundField
from nct.utils.reactive.field_factory import FieldFactory
class ReactiveModel(object):
    INSTRUMENT = 'Instrument'
    TRADE = 'Trade'
    FIELD_DEPENDS = { }

    def __init__(self):
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

