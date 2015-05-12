from datetime import date, datetime
import inspect
from nct.utils.reactive.common import InvalidModelError,\
    InvalidFieldDefinitionlError
from decimal import Decimal

DATATYPE_CONVERTERS = {(str,date):lambda value: datetime.strptime(value, "%Y-%m-%d").date()}

def error_help(datatype):
    error_help = {date:'YYYY-MM-DD format',
                  Decimal: "Numeric"}
    return error_help.get( datatype, datatype.__class__.__name__)

class DataTypeConversionError(Exception): pass

class BoundField:
    TO = 'TO'
    FROM = 'FROM'
    __slots__ = ('definition', 'value', 
                 'has_value', 'has_user_entered_value', 
                 'calculation_method', 'validation_method', 'domain_mapping_method', 'error' )
    
    def __init__(self, field_definition, model):
        self.definition = field_definition
        self.value = None
        self.has_value = False
        self.has_user_entered_value = False
        self.calculation_method = self._bind_method('calculation_method', model, 1)
        self.validation_method = self._bind_method('validation_method', model, 2)
        self.domain_mapping_method = self._bind_domain_mapping_method(model)
        self.error = None

    def _bind_method(self, method, model, arg_check):
        method_name = getattr(self.definition, method)
        if method_name:
            func = getattr(model, method_name, None)
            if not func:
                raise InvalidModelError( "%s is not defined in %s" % (method_name, model.__class__.__name__))
            arg_count = len(inspect.getargspec(func).args)
            if arg_check != arg_count:
                raise InvalidModelError("Wrong number of arguments to %s method.  Expected %s got %s" % (method_name, arg_check, arg_count))
            return func

    def set_value(self, value, user_entered=True):
        if value is None:
            self.value = None
            self.has_value = False
            self.has_user_entered_value = False
        else:  
            if not isinstance(value, self.definition.datatype):
                converter = DATATYPE_CONVERTERS.get((type(value),self.definition.datatype), self.definition.datatype )
                try:
                    self.value = converter(value)
                except:
                    raise DataTypeConversionError("Invalid value >{}< needs to be {}".format(value, error_help(self.definition.datatype)))
            else:
                self.value =  value
                
            self.has_value = True
            self.has_user_entered_value = user_entered

    def recalc(self):
        if not self.has_user_entered_value:
            if self.calculation_method:
                try:
                    self.set_value(self.calculation_method(), user_entered=False)
                    return True
                except Exception as e:
                    self.error = str(e)
        return False
   
    def validate(self):
        if self.validation_method:
            return self.validation_method(self)
    
    @property
    def name(self):
        return self.definition.name

    def _bind_domain_mapping_method(self, model):
        mapping = self.definition.domain_mapping
        if not mapping:
            return
        split_map = mapping.split(".")
        if len(split_map) == 1:
            return self._bind_method('domain_mapping', model, 3)
        elif len(split_map) == 2:
            if not getattr(model, 'get_domain_object', None):
                raise InvalidModelError ('%s does not support get_domain_object method' % model.__class__.__name__ )
            def mapper_function_wrapper(field, direction):
                domain_object = model.get_domain_object(split_map[0])
                if direction == self.TO:
                    setattr(domain_object,split_map[1],field.value )
                else:
                    return getattr(domain_object,split_map[1])
            return mapper_function_wrapper
        else:
            raise InvalidFieldDefinitionlError("Invalid domain_mapping %s for field %s" % ( mapping, self.name ) )
   
    def map_to_domain(self):
        if self.domain_mapping_method:
            self.domain_mapping_method(self, self.TO)

    def map_from_domain(self):
        if self.domain_mapping_method:
            self.set_value(self.domain_mapping_method(self, self.FROM))

