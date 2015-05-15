from nct.apps.csv_trade_loader import CSVTradeLoader
from tests.perf.bulk_file_writer import TetstFileBuilder
import time
import cProfile
import functools
import random

def profile_method(file_name = None):
    def gen_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            f = func
            cProfile.runctx('f(*args,**kwargs)', globals(), locals(), file_name)
            print("Done writing")
        return wrapper
    return gen_wrapper
    
loaders = []
def run_once(loader = None):
    start = time.time()
    loader  = CSVTradeLoader.create_from_path(file_name)
    status = loader.run()
    loaders.append(loader)
    print ("It took {}. {}".format(time.time() - start, status))

@profile_method(file_name = r'c:\temp\profile_full3.out')
def run_last():
    run_once()
    print( "DONE LAST")
    
if __name__ == "__main__":
    start = time.time()
    file_name = r'c:\temp\bulk_csv{}.csv'.format(random.random())
    for _ in range(100):
        TetstFileBuilder.build(file_name, 1000, 'new')
        run_once()
    print ("Finished in {}.".format(time.time() - start))
#     run_last()
#     print ("Finished2")        