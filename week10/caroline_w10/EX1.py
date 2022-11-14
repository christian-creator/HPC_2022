#!/usr/bin/env python3
################################### PACKAGES ###################################

import subprocess
import os
import time
from joblib import Parallel, delayed
import math

translationTable = str.maketrans("atcg","tagc")

#################################### INPUT #####################################

path2fsa = "humantest.fsa"

################################## FUNCTIONS ###################################

# Index function
def index_fasta(path):
    infile = open(path, 'rb')
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
    index = list()
    for i in range(len(headend)):
        index.append(f"{headend[i]+1} {headstart[i+1] - 1}")
    return index

# count function/worker
def kmer_fun (file, index, kmer_dicts):
    k = 5
    a_count = 0
    t_count = 0
    g_count = 0
    c_count = 0

    # Finding sequence
    seq_start, seq_end = index.split()

    with open(file, "r") as fi:
        fi.seek(int(seq_start))
        seq = fi.read(int(seq_end) - int(seq_start))

    # Appending kmers in dict
    for i in range(len(seq)):
        a_count += seq[i].count("a")
        t_count += seq[i].count("t")
        g_count += seq[i].count("g")
        c_count += seq[i].count("c")
        if "n" not in seq[i:i+k] and "\n" not in seq[i:i+k]:
            if seq[i:i+k] in kmer_dicts:
                kmer_dicts[seq[i:i+k]] += 1
            else:
                kmer_dicts[seq[i:i+k]] = 1

    return kmer_dicts, a_count, t_count, g_count, c_count


################################## EXECUTION ###################################

start_time = time.time()

kmer_dict = dict()

a_total = 0
t_total = 0
g_total = 0
c_total = 0
count = 0

if __name__ == '__main__':
    jobs = index_fasta(path2fsa)
    result = Parallel(n_jobs=2)(delayed(kmer_fun)(path2fsa, x, kmer_dict) for x in jobs)
    for res in result:
        a_total += res[1]
        t_total += res[2]
        g_total += res[3]
        c_total += res[4]

        # Merging dicts
        kmer_dict = {key: kmer_dict.get(key, 0) + res[0].get(key, 0) for key in res[0]}

    with open("kmer_overrepresentation.txt", "w") as fo:
        seq_len = a_total + t_total + g_total + c_total
        for kmer in kmer_dict.keys():
            P_n = list()
            for i in range(len(kmer)):
                if kmer[i] == "a":
                    P_n.append(a_total/seq_len)
                if kmer[i] == "t":
                    P_n.append(t_total/seq_len)
                if kmer[i] == "g":
                    P_n.append(g_total/seq_len)
                if kmer[i] == "c":
                    P_n.append(c_total/seq_len)

            # Calculating P(kmer)
            P_kmer = math.prod(P_n)

            if kmer_dict[kmer]/len(kmer_dict) > P_kmer:
                b = round(kmer_dict[kmer]/len(kmer_dict),7)
                fo.write(f"{kmer}: \t  {b} >  {P_kmer} \n")

print("Time:", time.time()-start_time)
