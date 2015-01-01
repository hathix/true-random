# uses the system PRNG to get a seed

import random

# returns a seed from 1-1000
def get_seed():
    floating = random.SystemRandom.random(random.SystemRandom())
    integer = int(floating * 1000)
    seed = integer

