
class ReactiveFramework:
    __slots__ = ('model', 'depends_notifty')
    def __init__(self, model):
        self.model = model
        self.depends_notifty = {}
        self._init_depends_notifty()
        self.model.bind_fields()
   
    def _init_depends_notifty(self):
        for field_name, deps in self.model.FIELD_DEPENDS.items():
            for dep_name in deps:
                self.depends_notifty.setdefault(dep_name, [])
                self.depends_notifty[dep_name].append(field_name)

    def _are_dependents_set(self, field_name):
        for dep_field in self.model.FIELD_DEPENDS[field_name]:
            if not getattr(self.model, dep_field).has_value:
                return False
        return True
   
    def _recalc_field(self, field_name, recalculated):
        if self._are_dependents_set(field_name):
            if getattr(self.model, field_name).recalc():
                recalculated.append(field_name)
                self._recalc_dependents(field_name, recalculated)

    def _recalc_dependents(self, field_name, recalculated=None):
        if recalculated is None:        
            recalculated = []
        for field in self.depends_notifty.get(field_name, []):
            if field not in recalculated:
                self._recalc_field(field, recalculated)
        return recalculated
       
    def set_value(self, field_name, value):
        getattr(self.model, field_name).set_value(value)
        return self._recalc_dependents(field_name)

    def get_value(self, field_name):
        return getattr(self.model, field_name).value

    def validate(self):
        result = {}
        for field in self.get_fields():
            errors = field.validate()
            if errors:
                result[field.name] = errors
        return result
    
    def get_fields(self):
        return [self.get_field( field_name) 
                  for field_name in self.model.FIELD_DEPENDS ]
        
    def get_field(self, field_name):
        return  getattr(self.model, field_name)

    def save(self):
        for field in self.get_fields():
            field.map_to_domain()
        return self.model.save()
        
    def load(self,trade_id):
        self.model.load(trade_id)
        
        for field in self.get_fields():
            field.map_from_domain()
        
        recalculated = []
        for field in self.get_fields():
            if not field.has_value:
                self._recalc_field(field.name, recalculated)
                
        for field in self.get_fields():
            field.has_user_entered_value = False
                
    def delete(self):
        self.model.delete()