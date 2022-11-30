#!/usr/bin/env python3
################################### PACKAGES ###################################

import math
import numpy as np
import sys, hashlib, time
from joblib import Parallel, delayed

#################################### INPUT #####################################

path2fsa = "/Users/carolinemartensen/Desktop/Caroline/DTU/9.semester/HPC/Exercises/W10/human.fsa"

mersize = 30

# The size of the bit field (the slice of bits taken from the hash)
bitfieldsize = 35 # your number that correlates with m.

# Translation table, borrowed from exercise solutions
toN = bytes.maketrans(b'MRYKVHDBacgtmrykvhdbxnsw',b'NNNNNNNNACGTNNNNNNNNNNNN')

# Bloom filter parameters from EX1
p = 0.008786073791150446
k = 4
m = 34359738368 
n = 3139742720

################################## FUNCTIONS ###################################

def hashit(kmer):
    myhashobj = hashlib.sha1()
    myhashobj.update(kmer)
    return int.from_bytes(myhashobj.digest(), byteorder=sys.byteorder)

def nextposition(hashnumber):
    position = hashnumber & (2**bitfieldsize - 1)
    byteposition = position >> 3
    bitposition = position & 7
    hashnumber >>= bitfieldsize # discarding the used hash slice
    return(hashnumber, byteposition, bitposition)

def setbit(bloomfilter, byteposition, bitposition):
    bloomfilter[byteposition] |= 1 << bitposition

# Indexing function from exercise solutions
def indexfasta(filename): 
    try:
        infile = open(filename, 'rb')
    except IOError as err:
        print("Cant open file:", str(err))
        sys.exit(1)
    chunksize = 1024*1024
    filepos = 0
    headstart = list()
    headend = list()
    while True:
        content = infile.read(chunksize)
        if len(content) == 0:
            break
        # find headers
        chunkpos = 0
        while chunkpos != -1:
            chunkpos = content.find(b'>', chunkpos)
            if chunkpos != -1:
                headstart.append(chunkpos + filepos)
                chunkpos += 1
        # find corresponding headend
        for i in range(len(headend), len(headstart)):
            chunkpos = max(0, headstart[i] - filepos)
            chunkpos = content.find(b'\n', chunkpos)
            if chunkpos != -1:
                headend.append(chunkpos + filepos)
        filepos += len(content)
    infile.close()
    # Eliminating wrong headers due to extra > in header line
    for i in range(len(headstart)-1, 0, -1):
        if headend[i] == headend[i-1]:
            del headstart[i]
            del headend[i]
    headstart.append(filepos)
    fastaindex = list()
    for i in range(len(headend)):
        fastaindex.append((headstart[i], headend[i], headend[i]+1, headstart[i+1] - 1))
    # sort the sequences according to size 
    fastaindex = np.array(fastaindex)
    sequence_length = np.array([])
    for i in range(len(fastaindex)):
        length = fastaindex[i][-1] - fastaindex[i][-2]
        sequence_length = np.append(sequence_length, int(length))
    indx = np.argsort(sequence_length)
    fastaindex = fastaindex[indx]
    return fastaindex

# Also from exercise solutions
def indexsequence(seq):
    pointer = 0
    seqindex = list()
    while len(seq) > pointer:
        # Find start of seq
        potenstart = [ seq.find(b'A', pointer), seq.find(b'T', pointer), seq.find(b'G', pointer), seq.find(b'C', pointer)]
        realstart = min(potenstart)
        if realstart == -1:
            # happens rarely, so slow code is ok
            potenstart = [ i for i in potenstart if i > -1 ]
            if len(potenstart) == 0:
                break
            realstart = min(potenstart)
        realend = seq.find(b'N', realstart)
        if realend == -1:
            realend = len(seq)
        if realend - realstart >= mersize:
            # realend is really 1 too large, but it is going to be used in a range
            seqindex.append((realstart, realend))
        pointer = realend
    return seqindex

# Function that checks if bit is set on given position. Returns bool.
def isbitset(bloomfilter, byteposition, bitposition):
    return (bloomfilter[byteposition] & (1 << bitposition)) != 0

# Function that creates the input in the bloom filter pr. sequence
def bytebit_str(seq):
    bytebit_pr_seq = ""
    seq = seq.translate(toN, b'\r\n\t ')
    idx_seq = indexsequence(seq)

    for seq_x in idx_seq:
        for i in range(seq_x[0], seq_x[1]-mersize+1):
            kmer = seq[i:i+mersize]
            hash_kmer = hashit(kmer)

            for i in range(k):
                hash_kmer, bytepos, bitpos = nextposition(hash_kmer)
                bytebit_pr_seq += str(bytepos) + "," + str(bitpos) + ","

    return bytebit_pr_seq

################################## EXECUTION ###################################

# Indexing the fasta file
idx_fsa = indexfasta(path2fsa)

try:
    infile = open(path2fsa, 'rb')
except IOError as err:
    print("Cant open file:", str(err))
    sys.exit(1)

# This attempt at parallelization was not successful. As it is not memory efficient. 
# So, I have only been able to run it on the smaller test-sets.
res = Parallel(n_jobs = 4)([delayed(bytebit_str)(infile.read(index[3]-index[2]+1)) for index in idx_fsa])

infile.close()

# Collecting the results from the parallelization
bloom_filter = bytearray(2**bitfieldsize)
for i in range(len(res)):
    bytebits = res[i].split(",")
    for j in range(0, len(bytebits)-2, 2):
        byte = int(bytebits[j])
        bit = int(bytebits[j+1])
        setbit(bloom_filter, byte, bit)

# Saving bloom filter in file 
file_bloomfilter = open("bloomfilter_final.txt", "wb")
file_bloomfilter.write(bloom_filter)
file_bloomfilter.close()
# Removing bloomfilter from memory
del bloom_filter      

