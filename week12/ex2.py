#!/usr/bin/env python3
import sys, hashlib
import subprocess
from joblib import Parallel, delayed

# The size of the bit field (the slice of bits taken from the hash)
bitfieldsize = 35 # your number that correlates with m.
K = 4

if len(sys.argv) != 2:
    print("Usage: ex2.py <input fasta file>");
    sys.exit(1)

input_fasta = sys.argv[1]

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
        yield (headstart, headend, seqstart, seqend)

def hash_kmer(kmer):
    hash_int = int.from_bytes(hashlib.sha1(kmer).digest(), 
                                    byteorder=sys.byteorder)
    for k in range(K): 
        position = hash_int & (2**bitfieldsize - 1)
        byteposition = position >> 3
        bitposition = position & 7
        yield (byteposition, bitposition)
        hash_int >>= bitfieldsize # discarding the used hash slice

def entry_bloomfilter(fasta_index, filename):
    KMER_LENGTH = 30

    header_start, header_end, seq_start, seq_end = fasta_index

    bloomfilter = bytearray(2**(bitfieldsize-3))

    with open(input_fasta, "rb") as f:
        # get header and sequence
        f.seek(int(header_start))
        header = f.read(int(header_end) - int(header_start)+1)
        f.seek(int(seq_start))
        seq = f.read(int(seq_end) - int(seq_start)+1)
    
    seq = seq.replace(b"\n", b"") 
    
    if len(seq) < KMER_LENGTH:
        return
    
    mask = int(KMER_LENGTH * '11', 2)

    num = 0
    counter = KMER_LENGTH
    counter_max = len(seq)

    new_kmer = True

    # Consider that the time saved from the while loop counter skips
    # probably is lost (and more), if it doesn't happen often. Then the
    # C-like for loop is better.
    while counter < counter_max:
        if new_kmer:
            num = 0
            new_kmer = False
            for i, char in enumerate(seq[counter - KMER_LENGTH : counter]):
                num <<= 2
                #a, t, c, g
                if char == 97:
                    pass
                elif char == 116:
                    num |= 0b11
                elif char == 99:
                    num |= 0b01
                elif char == 103:
                    num |= 0b10
                else:
                    new_kmer = True
                    counter += i + 1
                    break
            if new_kmer:
                continue
        else:
            char = seq[counter]
            num <<= 2
            #a, t, c, g
            if char == 97:
                pass
            elif char == 116:
                num |= 0b11
            elif char == 99:
                num |= 0b01
            elif char == 103:
                num |= 0b10
            else:
                new_kmer = True
                counter += KMER_LENGTH
            num &= mask

        counter += 1
        for byteposition, bitposition in hash_kmer(repr(num).encode()):
            bloomfilter[byteposition] |= 1 << bitposition

    with open(filename, "wb") as f:
        f.write(bloomfilter)

    return filename


N_JOBS = 8

file_name_prefix = "human_bloomfilter"

#run the parallel
result = Parallel(n_jobs=N_JOBS, verbose=69)(delayed(entry_bloomfilter)(index, f"{file_name_prefix}_{i}") for i, index in enumerate(index_fasta(input_fasta)))


#postprocessing
from operator import or_
import functools

n_files = len(result)

def bloom_filter_files(result):
    for res in result:
        with open(res, "rb") as f:
            yield int.from_bytes(f.read(), 'big')

final_bloomfilter = functools.reduce(or_, bloom_filter_files(result)).to_bytes(2**(bitfieldsize-3), 'big')

with open(file_name_prefix, "wb") as f:
        f.write(final_bloomfilter)

import os
for res in result:
    os.remove(res)

"""
time ./ex2.py ~/human.fsa
[Parallel(n_jobs=8)]: Using backend LokyBackend with 8 concurrent workers.
[Parallel(n_jobs=8)]: Done   1 tasks      | elapsed: 19.4min
[Parallel(n_jobs=8)]: Done   2 tasks      | elapsed: 21.1min
[Parallel(n_jobs=8)]: Done   3 tasks      | elapsed: 22.4min
[Parallel(n_jobs=8)]: Done   4 tasks      | elapsed: 24.0min
[Parallel(n_jobs=8)]: Done   5 tasks      | elapsed: 25.7min
[Parallel(n_jobs=8)]: Done   6 tasks      | elapsed: 27.0min
[Parallel(n_jobs=8)]: Done   7 tasks      | elapsed: 31.4min
[Parallel(n_jobs=8)]: Done   8 tasks      | elapsed: 31.8min
[Parallel(n_jobs=8)]: Done   9 tasks      | elapsed: 35.8min
[Parallel(n_jobs=8)]: Done  10 out of  24 | elapsed: 39.1min remaining: 54.7min
[Parallel(n_jobs=8)]: Done  11 out of  24 | elapsed: 39.3min remaining: 46.4min
[Parallel(n_jobs=8)]: Done  12 out of  24 | elapsed: 39.3min remaining: 39.3min
[Parallel(n_jobs=8)]: Done  13 out of  24 | elapsed: 40.4min remaining: 34.2min
[Parallel(n_jobs=8)]: Done  14 out of  24 | elapsed: 41.7min remaining: 29.8min
[Parallel(n_jobs=8)]: Done  15 out of  24 | elapsed: 42.8min remaining: 25.7min
[Parallel(n_jobs=8)]: Done  16 out of  24 | elapsed: 43.0min remaining: 21.5min
[Parallel(n_jobs=8)]: Done  17 out of  24 | elapsed: 45.9min remaining: 18.9min
[Parallel(n_jobs=8)]: Done  18 out of  24 | elapsed: 46.9min remaining: 15.6min
[Parallel(n_jobs=8)]: Done  19 out of  24 | elapsed: 47.0min remaining: 12.4min
[Parallel(n_jobs=8)]: Done  20 out of  24 | elapsed: 47.1min remaining:  9.4min
[Parallel(n_jobs=8)]: Done  21 out of  24 | elapsed: 47.1min remaining:  6.7min
[Parallel(n_jobs=8)]: Done  22 out of  24 | elapsed: 48.0min remaining:  4.4min
[Parallel(n_jobs=8)]: Done  24 out of  24 | elapsed: 61.9min remaining:    0.0s
[Parallel(n_jobs=8)]: Done  24 out of  24 | elapsed: 61.9min finished

real	66m59.553s
user	392m47.518s
sys	5m38.954s
"""


