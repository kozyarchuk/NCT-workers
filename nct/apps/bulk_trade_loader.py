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
        
class RecordProcessor:
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
        self.populate_rf()
        self.validate_rf()
        self.save()

    def create_rf(self):
        if not self.record.get('TradeType'):
            self.errors =  "TradeType must be specified"
            return

        self._rf = ReactiveFramework(VanillaModel())

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
                status.add_failure(str(e), record)
                
        return status 

    