from nct.utils.reactive.framework import ReactiveFramework
from nct.presentation.vanilla import VanillaModel

class BulkTradeLoadStatus:

    def __init__(self):
        self.total = 0
        self.loaded = 0
        self.errors = 0
        self.failed = 0
        self.rejected_trades = []
        
    def _add_reject(self, message, record):
        record['Status'] = message
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
    FIELD_MAP = [ ("Action",'action'),  
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

    def process(self):
        self.create_rf()
        self.populate_rf()
        self.validate_rf()
        self.save()

    def create_rf(self):
        if 'TradeType' not in self.record:
            self.errors =  "TradeType must be specified"

        self._rf = ReactiveFramework(VanillaModel())

    def populate_rf(self):
        if self.errors:
            return
        for external_name, internal_name in self.FIELD_MAP:
            value = self.record.get(external_name)
            if value:
                self._rf.set_value(internal_name, value)

    def validate_rf(self):
        if self.errors:
            return
        errors = self._rf.validate()
        self.errors  = ", ".join(["{!r}: {!r}".format(self.REV_MAP[field], value) 
                                  for field, value in sorted(errors.items())])

    def save(self):
        if self.errors:
            return
        self._rf.save()

        
class BulkTradeLoader:

    def load(self, records):
        status =  BulkTradeLoadStatus()
        for record in records:
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

    