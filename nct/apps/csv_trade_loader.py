import csv
from nct.apps.bulk_trade_loader import BulkTradeLoader, BulkTradeLoadStatus
import os
import tempfile

class CSVLoaderError(Exception):
    pass

class CSVTradeLoader(object):
    
    def __init__(self, file_root, source = None, output = None):
        self.file_root = file_root
        self.source = source if source else os.getcwd()
        self.output = output if output else tempfile.gettempdir()
    
    @property
    def trade_file(self):
        return self.file_root + ".csv"
    
    @property
    def error_file(self):
        return self.file_root + "_errors.csv"

    @property
    def error_filepath(self):
        return os.path.join( self.output, self.error_file)
    
    def load_trade_file(self):
        trades = []
        fields = []
        with open(os.path.join(self.source, self.trade_file), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if not fields:
                    fields = row
                else:
                    trades.append(dict((f,v) for f,v in zip(fields,row)))
        return fields, trades

    def write_csv(self,file_name, header, records):
        with open(file_name, 'w') as f:
            writer = csv.DictWriter(f, header)
            writer.writeheader()
            writer.writerows(records)  
        print ("Wrote {} records to {}".format(len(records), file_name ))  
        
    def run(self):
        fields, trades = self.load_trade_file()
        if BulkTradeLoadStatus.STATUS_FIELD not in fields:
            fields.append(BulkTradeLoadStatus.STATUS_FIELD)
        status = BulkTradeLoader(trades).load()
        self.write_csv(self.error_filepath, fields, status.rejected_trades)
        
    
    @classmethod
    def create_from_path(cls, file_path):
        folder, file_name = os.path.split(file_path)
        file_root, ext = os.path.splitext(file_name) 
        if ext != '.csv':
            raise CSVLoaderError("Invalid extension %s only .csv is allowed" % ext)
        return cls(file_root, folder, folder )
    