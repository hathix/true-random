# uses the system time (in millis) to get a seed

from datetime import datetime

# returns a seed from 1-1000
def get_seed():
    now = datetime.now()
    seed = now.microsecond; #seed
    return seed
