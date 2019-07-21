#!/usr/bin/python3.6

import os
import numpy as np

def randomDomain(path):
    domains = os.listdir("stp_domains/test/")
    index = np.random.random_integers(0, len(domains) - 1)
    return domains[index].split('.')[0]


