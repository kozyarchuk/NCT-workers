from nct.utils.alch import Session, LSession
from nct.domain.instrument import Instrument
import random
import functools
import time
from nct.deploy.deploy import Deployer
import cProfile

INSTRUMENTS = ['GOOGL.O', 'TWTR.N', 'GS.N', 'BAC.N', 'IBM.N']

def profile_method(file_name = None):
    def gen_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            f = func
            cProfile.runctx('f(*args,**kwargs)', globals(), locals(), file_name)
            print("Done writing")
        return wrapper
    return gen_wrapper
    
def time_it(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args,**kwargs)
        print("It took {}".format(time.time() - start))
    return wrapper

HASH_CACHE = {}

@profile_method(r"c:\temp\instrument_123.out")
def do_a_bunch():
    s = LSession()
    name = INSTRUMENTS[int(random.random()*100)%len(INSTRUMENTS)]
    instr_id = s.query(Instrument).filter_by(name=name).one().id
    for _ in range(10000):
        s.query(Instrument).get(instr_id)
    s.close()

import sys
print (sys.version)
Deployer(LSession).deploy()
print ("Deployed")
for _ in range(1):
    do_a_bunch()
