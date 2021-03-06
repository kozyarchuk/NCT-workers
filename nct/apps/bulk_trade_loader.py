from nct.utils.reactive.framework import ReactiveFramework
from nct.presentation.vanilla import VanillaModel

class BulkTradeLoadStatus:
    STATUS_FIELD = 'Status'
    def __init__(self):
        self.total = 0
        self.loaded = 0
        self.errors = 0
        self.failed = 0
        self.rejected_trades = []
        
    def _add_reject(self, message, record):
        record[self.STATUS_FIELD] = message
        self.rejected_trades.append(record)

    def add_error(self, message, record):
        self.errors += 1
        self._add_reject(message, record)

    def add_failure(self, message, record):
        self.failed += 1
        self._add_reject(message, record)

    def add_success(self):
        self.loaded += 1

    def add_total(self):
        self.total += 1
      
    def __repr__(self):
        return "<BulkLoadStatus: total={}, loaded={}, failed={}, errors={} >".format(self.total, self.loaded,self.failed, self.errors) 
    
class RecordProcessor:
    MSG_TYPE = "Msg Type"
    TRADE_ID = "Trade ID"
    TRADE_TYPE = "TradeType"
    MSG_TYPE_VALUES = ['New', 'Edit','Cancel']
    # FieldMap is represented as ordered list of tuples
    # to ensure repeatability of order in which values are set
    # on rf.
    FIELD_MAP = [  ("Trade ID",'trade_id'),  
                 ("Action",'action'),  
                 ('Quantity','quantity'),
                 ('Price','price'),
                 ('Instrument','instrument'),
                 ('Currency','currency'),
                 ('Trade Date', "trade_date"),
                 ('Settle Date', "settle_date"),
                 ('Fund', "fund"),
                 ('Trader', "trader"),
                 ('Analyst', "analyst"),
                 ('Broker', "broker"),
                 ('Clearer', "clearer"),
                 ('Sector', "sector"),
                 ('Strategy', "strategy"),
                 ]
    REV_MAP = dict( (domain_field,csv_field) 
                   for (csv_field,domain_field) in FIELD_MAP )

    def __init__(self, record):
        self.record = record
        self._rf = None
        self.errors = ''

    def _format_errors(self, errors):
        return ", ".join(["{!r}: {!r}".format(self.REV_MAP.get(field,field), value) for 
                (field, value) in sorted(errors.items())])

    def process(self):
        self.create_rf()
        if self.is_cancel():
            self.delete()
        else:
            self.populate_rf()
            self.validate_rf()
            self.save()

    @classmethod
    def model_list(cls):
        return [VanillaModel]
    
    @classmethod
    def get_model(cls, trade_type):
        for model in cls.model_list():
            model_name = model.model_name().lower()
            if model_name == trade_type.lower():
                return model
        
        
    @property
    def msg_type(self):
        return self.record.get(self.MSG_TYPE, "").lower()

    is_new = lambda  self: self.msg_type == "new"
    is_edit = lambda self: self.msg_type == "edit"
    is_cancel = lambda  self: self.msg_type == "cancel"

    def create_rf(self):
        errors = {}
        if not self.record.get(self.TRADE_ID):
            errors[self.TRADE_ID] = 'must be specified'

        model_klass = RecordProcessor.get_model(self.record.get(self.TRADE_TYPE,""))
        if not model_klass:
            errors[self.TRADE_TYPE] = 'Valid values for {} are [{}]'.format(self.TRADE_TYPE, ",".join([m.model_name() for m in self.model_list()]))
        
        if not any([self.is_cancel(), self.is_edit(), self.is_new()]):
            errors[self.MSG_TYPE] =  'Valid Msg Types are {}'.format(",".join(self.MSG_TYPE_VALUES))
        
        rf = None        
        if not errors:
            rf = ReactiveFramework(model_klass())
             
            loaded = rf.load(self.record[self.TRADE_ID])
            if loaded:
                if self.is_new():
                    errors[self.MSG_TYPE] = "{} already exists".format(self.TRADE_ID)
            else:
                if self.is_cancel() or self.is_edit():
                    errors[self.MSG_TYPE] = "{} does not exist".format(self.TRADE_ID)
            
        self.errors = self._format_errors(errors)
        if self.errors:
            return
        
        self._rf = rf

    def populate_rf(self):
        if self.errors:
            return
        errors = {}
        for external_name, internal_name in self.FIELD_MAP:
            value = self.record.get(external_name)
            if value:
                try:
                    self._rf.set_value(internal_name, value)
                except Exception as e:
                    errors[internal_name] =  str(e)
        self.errors  = self._format_errors(errors)
            
    def validate_rf(self):
        if self.errors:
            return
        errors = self._rf.validate()
        self.errors  = self._format_errors(errors)

    def save(self):
        if self.errors:
            return
        self._rf.save()

    def delete(self):
        if self.errors:
            return
        self._rf.delete()

        
class BulkTradeLoader:

    def __init__(self, records):
        self.records = records
        
    def load(self):
        status =  BulkTradeLoadStatus()
        for record in self.records:
            rp = RecordProcessor(record)
            status.add_total()
            try:
                rp.process()
                if rp.errors:
                    status.add_error(rp.errors, rp.record)
                else:
                    status.add_success()
            except Exception as e:
                import traceback;
                print (traceback.format_exc())
                status.add_failure(str(e), record)
        return status 

    