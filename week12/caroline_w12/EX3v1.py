#!/usr/bin/env python3
################################### PACKAGES ###################################

import math
import numpy as np
import sys, hashlib, time
from joblib import Parallel, delayed
import subprocess

#################################### INPUT #####################################

path2fsa = "/Users/carolinemartensen/Desktop/Caroline/DTU/9.semester/HPC/Exercises/W10/humantest.fsa"

mersize = 30

# Bloom filter parameters from EX1
p = 0.008786073791150446
k = 4
m = 34359738368
n = 3139742720

# The size of the bit field (the slice of bits taken from the hash)
bitfieldsize = 35 # your number that correlates with m.

# Translation table
toN = bytes.maketrans(b'MRYKVHDBacgtmrykvhdbxnsw',b'NNNNNNNNACGTNNNNNNNNNNNN')

############################ FUNCTIONS ############################

# Indexing function from solutions
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

# Function that returns bool if bit is set on the given position.
def isbitset(bloomfilter, byteposition, bitposition):
    return (bloomfilter[byteposition] & (1 << bitposition)) != 0


############################### EXECUTION ###################################

try:
    with open("bloomfilter_final.txt", "rb") as f:

        bloomfilter = bytearray()
        bloomfilter = f.read(-1)
except IOError:
    print('Error While Opening the file!')


path2test = "/Users/carolinemartensen/Desktop/Caroline/DTU/9.semester/HPC/Exercises/W12/mixeddna.fsa"
idx_test = indexfasta(path2test)
testfile = open(path2test, "rb")
sequence_ratio = []
complement = bytes.maketrans(b"ATCG", b"TAGC")

for i in range(len(idx_test)):
    print("Working on chromosome {}".format(i))
    no_of_hits = 0
    no_of_kmers = 0
    idx = idx_test[i]
    seq = testfile.read(idx[3]-idx[2]+1).translate(toN, b'\r\n\t ')
    for i in range(len(seq) - mersize + 1):
        kmer = seq[i:i+mersize]
        no_of_kmers += 1
        if b"N" in kmer:
            continue
        else:
            kmer_hash = hashit(kmer)
            reverse_kmer_hash = hashit(kmer.translate(complement)[::-1])
            for i in range(k):
                kmer_hash, bytepos, bitpos = nextposition(kmer_hash)
                if isbitset(bloomfilter, bytepos, bitpos):
                    no_of_hits += 1
                reverse_kmer_hash, bytepos, bitpos = nextposition(reverse_kmer_hash)
                if isbitset(bloomfilter, bytepos, bitpos):
                    no_of_hits += 1

    sequence_ratio.append(no_of_hits/no_of_kmers * 100)
testfile.close()


# Printing results
for i in range(len(sequence_ratio)):
    if sequence_ratio[i] > 95:
        print("Sequence {} is human. no_hits/no_kmers = {}".format(i+1,sequence_ratio[i]))
    else:
        print("Sequence {} is not human. no_hits/no_kmers = {}".format(i+1,sequence_ratio[i]))
