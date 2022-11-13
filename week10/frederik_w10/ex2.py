#!/usr/bin/env python3

import sys
import subprocess
from joblib import Parallel, delayed
from collections import defaultdict

if len(sys.argv) != 2:
    print("Usage: ex2.py <input fasta file>");
    sys.exit(1)

input_fasta = sys.argv[1]
#output_fasta_index = "fasta.idx"

def index_fasta(input_fasta):
    try:
        infile = open(input_fasta, 'rb')
    except IOError as err:
        print("Cant open file:", str(err));
        sys.exit(1)

    chunksize = 1024*1024 # 1 MB
    filepos = 0
    headers = list()
    newlines = list()

    while True:
        content = infile.read(chunksize)
        if len(content) == 0:
            break
        # find headers
        chunkpos = 0
        while chunkpos != -1:
            chunkpos = content.find(b'>', chunkpos)
            if chunkpos != -1:
                headers.append(chunkpos + filepos)
                chunkpos += 1
        # find corresponding newlines
        for i in range(len(newlines), len(headers)):
            chunkpos = max(0, headers[i] - filepos)
            chunkpos = content.find(b'\n', chunkpos)
            if chunkpos != -1:
                newlines.append(chunkpos + filepos)
        filepos += len(content)
    infile.close()

    # printing 
    for i in range(len(headers)):
        headstart = headers[i]
        headend = newlines[i]
        seqstart = headend + 1
        if i < len(headers) - 1:
            seqend = headers[i+1] - 1
        else:
            seqend = filepos - 1
        print(headstart, headend, seqstart, seqend)
        yield (headstart, headend, seqstart, seqend)


def kmers(seq, k):
    for i in range(len(seq) - k):
        substring = seq[i:i+k]
        yield substring

def find_kmers(index, kmer_lengths):
    header_start, header_end, seq_start, seq_end = index
    kmer_dict_local = dict()
    for length in KMER_LENGTHS:
        kmer_dict_local[length] = defaultdict(int)


    with open(input_fasta, "r") as f:
        # get header and sequence
        f.seek(int(header_start))
        header = f.read(int(header_end) - int(header_start)+1)
        f.seek(int(seq_start))
        seq = f.read(int(seq_end) - int(seq_start)+1)
    
    seq = seq.replace("\n", "") 
    
    a, c, g, t = 0, 0, 0, 0
    
    a = seq.count('a')
    c = seq.count('c')
    g = seq.count('g')
    t = seq.count('t')

    for length in kmer_lengths:
        counter_stop = len(seq) - length
        for kmer in kmers(seq, length):
            kmer_dict_local[length][kmer] += 1

    return kmer_dict_local, (a, c, g, t), len(seq)


KMER_LENGTHS = (5, 6, 7)
N_JOBS = 16

kmer_dict = dict()
keys = dict()
a, c, g, t = 0, 0, 0, 0
total_length = 0

for length in KMER_LENGTHS:
    kmer_dict[length] = defaultdict(int)
    keys[length] = set()

result = Parallel(n_jobs=N_JOBS, verbose=69)(delayed(find_kmers)(index, KMER_LENGTHS) for index in index_fasta(input_fasta))

for kmer_dict_local, base_counts, length_seq in result:
    for length in KMER_LENGTHS:
        keys[length] = keys[length].union(kmer_dict_local[length])
    a += base_counts[0]
    c += base_counts[1]
    g += base_counts[2]
    t += base_counts[3]
    total_length += length_seq

for length in KMER_LENGTHS:
    kmer_dict[length] = {i: sum(x.get(i, 0) for x in [y[length] for y, _, _ in result])
        for i in keys[length]}
    for key in keys[length]:
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




