#!/usr/bin/env python3

"""
OUTPUT:
10-mers only present once:  1
Unique 10-mers in file:  1048576
Max possible 10-mers:  1048576
Time: 907.1799669265747 (~ 15 min)
I find this a bit suspiciously fast, compared to the miserable attempt I had 
with the bytearray exercise. But never the less, I consider this a proud moment.
"""

################################### PACKAGES ###################################

import time
from joblib import Parallel, delayed
import numpy as np

#################################### INPUT #####################################


path2fsa = "/home/projects/pr_course/human.fsa"

mer_size = [10]

################################## FUNCTIONS ###################################

def seq_from_fasta(fasta_name):
    seq = list()
    with open(fasta_name, "r") as fsa:
        for line in fsa:
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
        if any([char not in 'acgt' for char in seq[i:i+k]]):
            pass
        else:
            yield seq[i:i+k]

# Putting kmers into a dictionary
def kmers_in_dict (seq, k_mer_length):
    kmer_dict = dict()
    # Counting the k-mers by itertating over generator K-mers.
    for kmer in kmer_generator(seq,k_mer_length):
        if kmer not in kmer_dict:
            kmer_dict[kmer] = 1
        else:
            kmer_dict[kmer] += 1

    return kmer_dict

################################## EXECUTION ###################################

start_time = time.time()

kmer_dict = dict()

if __name__ == '__main__':
    for i in range(len(mer_size)):
        result = Parallel(n_jobs = 7)(delayed(kmers_in_dict)(seq, mer_size[i]) for seq in seq_from_fasta(path2fsa))
        # Merging the dictionaries
        for dictionary in result:
            for key in dictionary.keys():
                if key in kmer_dict:
                    kmer_dict[key] += dictionary[key]
                else:
                    kmer_dict[key] = dictionary[key]

        # Printing results
        print(f"{mer_size[i]}-mers only present once: ", len([i for i in kmer_dict.values() if i == 1]))
        print(f"Unique {mer_size[i]}-mers in file: ", len([i for i in kmer_dict.values() if i > 0]))
        print(f"Max possible {mer_size[i]}-mers: ", 4**mer_size[i])

print("Time:", time.time()-start_time)