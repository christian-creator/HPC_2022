#!/usr/bin/env python3

"""
OUTPUT:
Elements in the bloom filter (n): 3139742720
Probability of false positives (p): 0.008786073791150446
Number of hash functions (k): 4
Size of the bit field (m): 34359738368
"""

################################### PACKAGES ###################################

import math
import numpy as np
import sys, hashlib, time
from joblib import Parallel, delayed
import subprocess

#################################### INPUT #####################################

# Initial probability, indicates the probability we want it lower than
p = 0.01

# Estimation of elements in the bloom filter
n = 3139742720
# n is estimated based on character-count for the human.fsa file. 

############################ BLOOM FILTER VARIABLES ############################

# Calculation of m
m = (-n*math.log(p))/(math.log(2)**2)
# correcting m in order to decrease error
for i in range(20,40):
    if 2**i >= m:
        pow2 = i
        break
m = 2**pow2

# Calculation of k (Number of hash functions)
k = math.ceil(abs(math.log(p)/math.log(2)))

# Checking if p is much lower than desired, in order to reduce the number of hash functions
p_update = (1-math.exp(-k*n/m))**k

# Checking if k can be reduced while p still is below 1%
for i in range(k):
    k_down = k - i 
    p_update = (1-math.exp(-k_down*n/m))**k_down
    # When p_update surpasses p, the loop needs to stop and the correct k and p can then be calculated
    if p_update > p:
        break

p_update = (1-math.exp(-(k_down+1)*n/m))**(k_down+1)
k = k_down + 1

# Printing results
print(f"Elements in the bloom filter (n): {n}")
print(f"Probability of false positives (p): {p_update}")
print(f"Number of hash functions (k): {k}")
print(f"Size of the bit field (m): {m}")