
from nct.apps.csv_trade_loader import CSVTradeLoader
from tests.perf.bulk_file_writer import TetstFileBuilder
import time
import cProfile
import functools
import random
import objgraph

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
def run_once(cnt):
#     DATA_CACHE.clear()
#     import gc
#     gc.collect()  # don't care about stuff that would be garbage collected properly
# #     tr.print_diff()      
# #     all_objects = muppy.get_objects()
# #     print(len(all_objects))
#     import objgraph
#     growth = objgraph.show_growth(limit=10)
#     if growth:
#         print ("I leaked{}".format( growth ) )
#     print(objgraph.show_most_common_types())
    start = time.time()
    loader  = CSVTradeLoader.create_from_path(file_name)
    status = loader.run()
#     loaders.append(loader)
    print ("{}. Took {}. {}".format(cnt, time.time() - start, status))


@profile_method(file_name = r'c:\temp\profile_first.out')
def run_first():
    run_once()
    print( "DONE FIRST")
    
@profile_method(file_name = r'c:\temp\profile_last.out')
def run_last():
    run_once("last")
    objgraph.show_chain(
            objgraph.find_backref_chain(
                random.choice(objgraph.by_type('BoundField')),
                objgraph.is_proper_module),
                filename=r'c:\temp\chain.png')
    print( "DONE LAST")
    
if __name__ == "__main__":
    file_name = r'c:\temp\bulk_csv{}.csv'.format(random.random())
#     TetstFileBuilder.build(file_name, 1000, 'new')
#     run_first()
    start = time.time()
    for i in range(1000):
        TetstFileBuilder.build(file_name, 1000, 'new')
        run_once(i)
    print ("Finished in {}.".format(time.time() - start))
    TetstFileBuilder.build(file_name, 1000, 'new')
    run_last()
    print ("Finished2")        