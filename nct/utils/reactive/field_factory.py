import csv
import os
from nct.utils.reactive.field import Field
from decimal import Decimal
import datetime
from nct.utils.reactive.common import InvalidFieldDefinitionlError

class FieldFactory:
    _FIELDS = None    
    
    @classmethod
    def _convert_empty_string_to_none(cls, row):
        for k in row:
            if not row[k]:
                row[k] = None

    @classmethod
    def _set_datatype(cls, row):
        scope = {'Decimal':Decimal, 'datetime':datetime}
        row['datatype'] = eval(row['datatype'], scope, {})

    @classmethod
    def get_fields(cls):
        if cls._FIELDS is None:
            cls._FIELDS = []
            with open(os.path.join(os.path.dirname(__file__), 'fields.csv')) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cls._set_datatype(row)
                    cls._convert_empty_string_to_none(row)
                    cls._FIELDS.append(Field(**row))
        return cls._FIELDS
    
    @classmethod
    def get_field(cls, field_name):
        for field in cls.get_fields():
            if field.name == field_name:
                return field
        raise InvalidFieldDefinitionlError('%s is not a valid field' % field_name)

