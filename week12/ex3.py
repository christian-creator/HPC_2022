#!/usr/bin/env python3
import sys, hashlib

# The size of the bit field (the slice of bits taken from the hash)
bitfieldsize = 35 # your number that correlates with m.
K = 4

def hash_kmer(kmer):
    hash_int = int.from_bytes(hashlib.sha1(kmer).digest(), 
                                    byteorder=sys.byteorder)
    for k in range(K): 
        position = hash_int & (2**bitfieldsize - 1)
        byteposition = position >> 3
        bitposition = position & 7
        yield (byteposition, bitposition)
        hash_int >>= bitfieldsize # discarding the used hash slice

import sys
import subprocess
from joblib import Parallel, delayed


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


def entry_bloomfilter(fasta_index, bloomfilter_file):
    KMER_LENGTH = 30

    header_start, header_end, seq_start, seq_end = fasta_index

    with open(input_fasta, "rb") as f:
        # get header and sequence
        f.seek(int(header_start))
        header = f.read(int(header_end) - int(header_start)+1)
        f.seek(int(seq_start))
        seq = f.read(int(seq_end) - int(seq_start)+1)
    
    seq = seq.replace(b"\n", b"") 
    
    if len(seq) < KMER_LENGTH:
        return
    
    with open(bloomfilter_file, "rb") as f:
        bloomfilter = f.read()

    mask = int(KMER_LENGTH * '11', 2)

    num = 0
    counter = KMER_LENGTH
    counter_max = len(seq)

    no_of_hits = no_of_kmers = 0

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
        no_of_kmers += 1
        if all((bloomfilter[byteposition] & (1 << bitposition)) != 0 for byteposition, bitposition in hash_kmer(repr(num).encode())):
            no_of_hits += 1


    return no_of_hits, no_of_kmers


N_JOBS = 8

#file_name_prefix = "test_bloom"
file_name_prefix = "human_bloomfilter"

#run the parallel
result = Parallel(n_jobs=N_JOBS, verbose=69)(delayed(entry_bloomfilter)(index, file_name_prefix) for i, index in enumerate(index_fasta(input_fasta)))


#postprocessing
no_of_hits_array, no_of_kmers_array = zip(*result)
no_of_hits = sum(no_of_hits_array)
no_of_kmers = sum(no_of_kmers_array)

if no_of_kmers == 0:
    print("Error: files contains no valid k-mers (lowercase atcg).")
    sys.exit(1)

print(f'No of hits: {no_of_hits}')
print(f'No of kmers: {no_of_kmers}')
print(f'Percentage match: {no_of_hits/no_of_kmers*100}%')

"""
./ex3.py ~/pr_course/humantest.fsa 
No of hits: 1596458
No of kmers: 1596458
Percentage match: 100.0%

./ex3.py mixeddna_lower.fsa 
No of hits: 0
No of kmers: 51691
Percentage match: 0.0%
"""





