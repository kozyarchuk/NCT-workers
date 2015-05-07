
class Field:
    def __init__(self, name, datatype, validation_method=None, 
                 calculation_method=None, domain_mapping = None):
        self.name = name
        self.datatype = datatype
        self.validation_method = validation_method
        self.calculation_method = calculation_method
        self.domain_mapping = domain_mapping
        