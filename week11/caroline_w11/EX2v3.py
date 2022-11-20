#!/usr/bin/env python3

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
    for i in range(len(seq)-k):
        yield seq[i:i+k]

# change seq to byte
def dna2num(seq):
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
    bytearray_fun = bytearray(4**mer_size[i])

    with open(path2fsa, 'r') as fasta:
        for seq in seq_from_fasta(fasta):
            print("kiwi")
            for kmer in kmer_generator(seq, mer_size[i]):
                if any([char not in 'acgt' for char in kmer]):
                    continue
                else:
                    for num_kmer in dna2num(kmer):
                        if bytearray_fun[num_kmer] < 2:
                            bytearray_fun[num_kmer] += 1

    # Printing results
    # Printing the ones which has a count of 1
    print(f"{mer_size[i]}-mers only present once: ", len([i for i in bytearray_fun if i == 1]))
    # Only printing the ones which has a count above 0
    print(f"Unique {mer_size[i]}-mers in file: ", len([i for i in bytearray_fun if i > 0]))
    # Printing the amount of possible kmers, when having the selected kmer size
    print(f"Max possible {mer_size[i]}-mers: ", 4**mer_size[i])

print("Time:", time.time()-start_time)