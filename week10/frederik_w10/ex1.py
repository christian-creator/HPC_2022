#!/usr/bin/env python3

import sys
from collections import defaultdict
import re

not_acgt = re.compile(r'[^acgt]')

if len(sys.argv) == 2:
    fasta_file = sys.argv[1]
else:
    print("Must specifiy exactly one argument: fasta file.")
    sys.exit(1)

def fasta_entries(fp):
    name, seq = None, []
    for line in fp:
        line = line.rstrip()
        if line.startswith('>'):
            if name:  
                yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)
    if name: yield (name, ''.join(seq))

def kmers(seq, k):
    for i in range(len(seq) - k):
        substring = seq[i:i+k]
        yield substring

kmer_dict = dict()
KMER_LENGTHS = (5, 6, 7)
for length in KMER_LENGTHS:
    kmer_dict[length] = defaultdict(int)

a, c, g, t = 0, 0, 0, 0
total_length = 0

with open(fasta_file, "r") as f:
    for name, seq in fasta_entries(f):
        a += seq.count('a')
        c += seq.count('c')
        g += seq.count('g')
        t += seq.count('t')
        total_length += len(seq)
        for length in KMER_LENGTHS:
            counter_stop = len(seq) - length
            for kmer in kmers(seq, length):
                kmer_dict[length][kmer] += 1

for length in KMER_LENGTHS:
    keys = list( kmer_dict[length].keys())
    for key in keys:
        if any([char not in 'acgt' for char in key]):
            del kmer_dict[length][key]

p = dict()
p["a"] = a / total_length
p["c"] = c / total_length
p["g"] = g / total_length
p["t"] = t / total_length
print(p, total_length)


for length in KMER_LENGTHS:
    total_kmers = sum(kmer_dict[length].values())
    for substring, count in kmer_dict[length].items():
        p_substring = 1
        for char in substring:
            p_substring *= p[char]
        #print(substring, count/total_kmers, p_substring, length)
        if count / total_kmers > 1.4 * p_substring:
            print((count / total_kmers) / p_substring)
            print(substring, count, length)


