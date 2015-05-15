import random
from _decimal import Decimal
from nct.apps.csv_trade_loader import CSVTradeLoader
INSTRUMENTS = ['GOOGL.O', 'TWTR.N', 'GS.N', 'BAC.N', 'IBM.N']
    
ACTIONS = ["Buy", "Sell"]
default_record = {"Quantity": Decimal(100),
                  "Price":Decimal(22),
                  "Action":"Buy",
                  "Trade Date":"2015-01-01",
                  "Instrument": "GOOGL.O",
                  "Fund": "Fund1",
                  "TradeType":"Vanilla",
                  "Trade ID": 1,
                  "Msg Type":"new"
                  }

class TetstFileBuilder:
    
    @classmethod
    def build(self, file_name, number):
        ID_BASE = hash(random.random())
        header = default_record.keys()
        records = []
        for i in range(number):
            rec = default_record.copy()
            rnd = Decimal("{:5f}".format( random.random() ))
            rec['Price'] = round(rec['Price'] * rnd*2, 5)
            rec['Quantity'] = round(rec['Quantity'] * rnd*2 +1, 0)
            rec['Instrument'] = INSTRUMENTS[int(rnd*100)%len(INSTRUMENTS)]
            rec['Trade ID'] = "{}-{}".format(ID_BASE, i)
            records.append(rec)

        CSVTradeLoader.write_csv(file_name, header, records)

if __name__ == "__main__":
    file_name = r'c:\temp\bulk_csv.csv'
    TetstFileBuilder.build(file_name, 5)