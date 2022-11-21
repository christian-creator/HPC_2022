#!/usr/bin/env python3

"""
OUTPUT
10-mers only present once:  1
Unique 10-mers in file:  1048576
Max possible 10-mers:  1048576
Time: 825.9441595077515 ~ 14 min

This exercise was finished after hearing CPs method for merging bytearrays,
which is why it was handed in after the other two :)
"""
################################### PACKAGES ###################################

import time
from joblib import Parallel, delayed
import numpy as np
import sys

#################################### INPUT #####################################

path2fsa = "/home/projects/pr_course/human.fsa"

mer_size = [10]

################################## FUNCTIONS ###################################

# Make generator that separates the sequences in the fasta file
# Personal note: Yield is used when creating generators, it manages the flow of the generator, to avoid storing things in memory. Great for big data, such as this.
def seq_from_fasta(fasta_name):
    seq = list()
    for line in fasta_name:
        if line.startswith('>'):
            if seq:
                yield ''.join(seq)
            seq = []
        else:
            seq.append(line.strip())
    if seq:
        yield ''.join(seq)

# Kmer generator
def kmer_generator(seq, k):
    bytearray_fun = bytearray(4**k)

    for i in range(len(seq)-k):
        if any([char not in 'acgt' for char in seq[i:i+k]]):
                    pass
        else:
            for num_kmer in dna2num(seq[i:i+k], k):
                if bytearray_fun[num_kmer] < 2:
                    bytearray_fun[num_kmer] += 1

    return bytearray_fun

# Make function that can do what dna2num does
def dna2num(seq, mer_size):
    num = 0
    for char in seq:
        # Bitshift two bits to the left
        num <<= 2
        if char == 'a':
            pass
        elif char == 't':
            num |= 0b11
        elif char == 'c':
            num |= 0b01
        elif char == 'g':
            num |= 0b10
        else:
            print("Illegal base in DNA sequence")
            sys.exit(1)

    yield num

################################## EXECUTION ###################################

start_time = time.time()

for i in range(len(mer_size)):
    bytearray_total = bytearray(4**mer_size[i])

    with open(path2fsa, 'r') as fasta:
        results = Parallel(n_jobs=-1)(delayed(kmer_generator)(seq, mer_size[i]) for seq in seq_from_fasta(fasta))

    for j in range(len(bytearray_total)):
        for res in results:
            bytearray_total[j] += res[j]


    # Filtering results
    singular_kmer = list(filter(lambda x: x == 1, bytearray_total))
    unique_kmer = len(list(filter(lambda x: x > 0, bytearray_total)))

    # Printing results
    print(f"{mer_size[i]}-mers only present once: ", len(singular_kmer))
    print(f"Unique {mer_size[i]}-mers in file: ", unique_kmer)
    print(f"Max possible {mer_size[i]}-mers: ", 4**mer_size[i])

print("Time:", time.time()-start_time)
