import unittest
from nct.utils.reactive.field import Field
from nct.utils.reactive.field_factory import FieldFactory
from decimal import Decimal
import datetime
from nct.utils.reactive.bound_field import BoundField, InvalidModelError,\
    InvalidFieldDefinitionlError
from nct.utils.reactive.framework import ReactiveFramework

class FieldTest(unittest.TestCase):

    def test_field_construction(self):
        f = Field(name = "f1", 
                  datatype = str, 
                  validation_method = 'vm', 
                  calculation_method = 'cm', 
                  domain_mapping = 'dm')
        
        self.assertEquals("f1", f.name)
        self.assertEquals(str, f.datatype)
        self.assertEquals("vm", f.validation_method)
        self.assertEquals("cm", f.calculation_method)
        self.assertEquals("dm", f.domain_mapping)

    def test_field_factory_loads_quantity(self):
        f = FieldFactory.get_field('quantity')
        self.assertEquals('quantity', f.name)
        self.assertEquals(Decimal, f.datatype)
        self.assertEquals(None, f.calculation_method)
        self.assertEquals('must_be_provided', f.validation_method)
        self.assertEquals('Trade.quantity', f.domain_mapping)

    def test_field_factory_loads_action(self):
        f = FieldFactory.get_field('action')
        self.assertEquals('action', f.name)
        self.assertEquals(str, f.datatype)
        self.assertEquals(None, f.calculation_method)
        self.assertEquals('must_be_provided', f.validation_method)
        self.assertEquals('Trade.action', f.domain_mapping)

    def test_field_factory_loads_trade_date(self):
        f = FieldFactory.get_field('trade_date')
        self.assertEquals('trade_date', f.name)
        self.assertEquals(datetime.date, f.datatype)
        self.assertEquals(None, f.calculation_method)
        self.assertEquals('must_be_provided', f.validation_method)
        self.assertEquals('Trade.trade_date', f.domain_mapping)

    def test_field_factory_missing_field(self):
        self.assertRaisesRegex(InvalidFieldDefinitionlError, 'invalid_field is not a valid field', FieldFactory.get_field, 'invalid_field')
    
    
class StubModel(object):
    FIELD_DEPENDS = {
                     'quantity':[]
                     }
    def val_meth(self, field):
        return "Validation Error"
    
    def calc_meth(self):
        return "123"
    
    def mapper(self, field, direction):
        if direction == field.TO:
            self.domain_value = field.value
        else:
            return self.domain_value

class BoundFieldTest(unittest.TestCase):
    
    def create_field(self):
        f = Field(name="f1", 
            datatype=Decimal, 
            validation_method='val_meth', 
            calculation_method='calc_meth', 
            domain_mapping='mapper')
        return f

    def test_can_create(self):
        f = self.create_field()
        m = StubModel()
        bf = BoundField(f , m)
        self.assertEquals(m.calc_meth, bf.calculation_method)
        self.assertEquals(m.val_meth, bf.validation_method)
        self.assertEquals(m.mapper, bf.domain_mapping_method)
        self.assertEquals(f, bf.definition )
        self.assertEquals('f1', bf.name)
        self.assertEquals(None, bf.value )
        self.assertEquals(False, bf.has_value)
        self.assertEquals(False, bf.has_user_entered_value)
        
    def test_bimd_method_checks_argument_count(self):
        f = self.create_field()
        m = StubModel()
        bf = BoundField(f , m)
        self.assertRaisesRegex(InvalidModelError, "Wrong number of arguments to calc_meth method.  Expected 3 got 1", bf._bind_method, 'calculation_method', m, 3)
        
    def test_bind_method_raises_error_if_method_is_missing_from_model(self):
        f = Field(name="f1", datatype=str,
            validation_method='method_is_missing')
        m = StubModel()
        self.assertRaisesRegex(InvalidModelError, "method_is_missing is not defined in StubModel", BoundField, f , m)

    def test_set_value_converts_datatype_and_set_value_flag(self):
        f = self.create_field()
        bf = BoundField(f , StubModel())
        bf.set_value("100.1")
        self.assertEquals(Decimal("100.1"), bf.value)
        self.assertEquals(True, bf.has_value)
        self.assertEquals(True, bf.has_user_entered_value)
        
    def test_set_value_does_not_set_user_entered_flag(self):
        f = self.create_field()
        bf = BoundField(f , StubModel())
        bf.set_value(Decimal("100.1"),user_entered=False)
        self.assertEquals(Decimal("100.1"), bf.value)
        self.assertEquals(True, bf.has_value)
        self.assertEquals(False, bf.has_user_entered_value)
        
    def test_set_value_unsets_value_on_none(self):
        f = self.create_field()
        bf = BoundField(f , StubModel())
        bf.set_value(Decimal("100.1"))
        bf.set_value(None)
        self.assertEquals( None, bf.value)
        self.assertEquals( False, bf.has_value)
        self.assertEquals( False, bf.has_user_entered_value)

    def test_recalc(self):
        f = self.create_field()
        bf = BoundField(f , StubModel())
        self.assertEquals(True, bf.recalc() )
        self.assertEquals(Decimal("123"), bf.value)
        bf.set_value("101")
        self.assertEquals(False, bf.recalc() )
        self.assertEquals(Decimal("101"), bf.value)

    def test_recalc_when_calc_method_is_none(self):
        f = Field(name="f1",  datatype=Decimal )
        bf = BoundField(f , StubModel())
        self.assertEquals(False, bf.recalc() )
        self.assertEquals(None, bf.value)

    def test_validate(self):
        f = self.create_field()
        bf = BoundField(f , StubModel())
        self.assertEquals( 'Validation Error', bf.validate() )

    def test_validate_when_val_meth_is_not_set(self):
        f = Field(name="f1",  datatype=Decimal )
        bf = BoundField(f , StubModel())
        self.assertEquals( None, bf.validate() )

    def test_bind_domain_mapping_method_when_no_mapping(self):
        f = Field(name="f1",  datatype=Decimal )
        bf = BoundField(f , StubModel())
        self.assertEquals( None, bf.domain_mapping_method )
        
    def test_bind_domain_mapping_method_when_invalid_mapping(self):
        f = Field(name="f1",  datatype=Decimal, domain_mapping="a.b.c" )
        self.assertRaisesRegex(InvalidFieldDefinitionlError, 'Invalid domain_mapping a.b.c for field f1', BoundField, f , StubModel())

    def test_bind_domain_mapping_direct_model_must_have_domain_object(self):
        f = Field(name="f1",  datatype=Decimal, domain_mapping="do.f1" )
        self.assertRaisesRegex(InvalidModelError, 'StubModel does not support get_domain_object method', BoundField, f , StubModel())

    def test_map_to_and_from_domain_using_direct_syntax(self):
        
        class DomainObject:
            f1 = 'aaa'
            
        do = DomainObject()
        f = Field(name="f1",  datatype=Decimal, domain_mapping="do.f1" )
        m = StubModel()
        m.get_domain_object = lambda name: do
        bf = BoundField( f , m)
        bf.set_value("123")
        bf.map_to_domain()
        self.assertEqual(Decimal("123"), do.f1)
        do.f1 = Decimal("456")
        bf.map_from_domain()
        self.assertEqual(Decimal("456"), bf.value)

    def test_map_to_and_from_domain_using_model_proxy(self):
        f = self.create_field()
        m = StubModel()
        bf = BoundField( f , m)
        bf.set_value("123")
        bf.map_to_domain()
        self.assertEqual(Decimal("123"), m.domain_value)
        m.domain_value = Decimal('456')
        bf.map_from_domain()
        self.assertEqual(Decimal("456"), bf.value)

    def test_map_to_and_from_domain_when_no_mapper(self):
        f = Field(name="f1",  datatype=Decimal )
        bf = BoundField(f , StubModel())
        bf.set_value("123")
        bf.map_to_domain()
        bf.set_value("456")
        bf.map_from_domain()
        self.assertEqual(Decimal("456"), bf.value)



