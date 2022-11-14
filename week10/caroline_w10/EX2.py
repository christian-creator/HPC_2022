#!/usr/bin/env python3
" Time: 14 min"
################################### PACKAGES ###################################

import time
from joblib import Parallel, delayed
import math
import numpy as np

#################################### INPUT #####################################

path2fsa = "/home/projects/pr_course/human.fsa"

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

# Checking that only the right characters are in the string
def contains_certain_characters(string, characters):
    return all(char in characters for char in string)

# Appending and counting kmers
def kmer_count(k,seq):
  f = {}
  for x in range(len(seq)+1-k):
      kmer = seq[x:x+k]
      f[kmer] = f.get(kmer, 0) + 1
  return f

# count function/worker
def kmer_fun (file, index, kmer_dicts):
    k = [5, 6, 7]
    for j in range(len(k)):
        kmer_len = k[j]
        a_count = 0
        t_count = 0
        g_count = 0
        c_count = 0

        # Finding sequence
        seq_start, seq_end = index.split()

        seq_time = time.time()
        with open(file, "r") as fi:
            fi.seek(int(seq_start))
            seq = fi.read(int(seq_end) - int(seq_start))

        a_count += seq.count("a")
        t_count += seq.count("t")
        g_count += seq.count("g")
        c_count += seq.count("c")

        # Appending kmers in dict
        kmer_dicts = kmer_count(kmer_len, seq)
    return kmer_dicts, a_count, t_count, g_count, c_count

################################# PARALLELIZE ##################################
# Here I am using the Least load method to separate the sequences into 4 groups
# As I am doing it based on the sequence there is still quite a big difference between some of the groups.
# This could have been solved by dividing the file into 4 equal sized chunks.
# However, I have not gotten that strategy farther than pseudocode :)
# I have chosen not to use either of my two load balancing methods.

"""
group1 = []
group2 = []
group3 = []
group4 = []
group1_len = 0
group2_len = 0
group3_len = 0
group4_len = 0

for idx in index_fasta(path2fsa):
    seq_start, seq_end = idx.split(" ")
    seq_len = float(seq_end)-float(seq_start)
    if group1_len == 0 and group2_len == 0 and group3_len == 0 and group4_len == 0:
        group1.append(idx)
        group1_len += seq_len
    elif group2_len == 0 and group3_len == 0 and group4_len == 0:
        group2.append(idx)
        group2_len += seq_len
    elif group3_len == 0 and group4_len == 0:
        group3.append(idx)
        group3_len += seq_len
    elif group4_len == 0:
        group4.append(idx)
        group4_len += seq_len
    if group1_len < group2_len and group1_len < group3_len and group1_len < group4_len:
        group1.append(idx)
        group1_len += seq_len
    elif group2_len < group1_len and group2_len < group3_len and group2_len < group4_len:
        group2.append(idx)
        group2_len += seq_len
    elif group3_len < group1_len and group3_len < group2_len and group3_len < group4_len:
        group3.append(idx)
        group3_len += seq_len
    elif group4_len < group1_len and group4_len < group2_len and group4_len < group3_len:
        group4.append(idx)
        group4_len += seq_len
print("Indexing + Grouping: ", time.time()-start_time)
"""
# This is my second attempt at separating them into groups, it turned out to be slower.. Please ignore :)
"""
# The length of the sequences added to the group are presented by the last element
group1 = [0]
group2 = [0]
group3 = [0]
group4 = [0]
count = 0
groups = [group1, group2, group3, group4]

def least_load_sort_index(index, count, groups):
    while True:
        if count >= len(index):
            return groups[0][:-1], groups[1][:-1], groups[2][:-1], groups[3][:-1]
            break

        # As the sequence length is the last element in the length, this sorts them based on length.
        group_size_index = np.argsort([groups[0][-1], groups[1][-1], groups[2][-1], groups[3][-1]])
        groups = np.array(groups, dtype=object)[group_size_index]
        groups = groups.tolist()

        # Pop out the sequence length in order to update it
        group_length = groups[0].pop(-1)
        # Calculating sequence length and appending index to group
        seq_start, seq_end = index[count].split(" ")
        groups[0].append(index[count])
        group_length = group_length + (int(seq_end)-int(seq_start))
        groups[0].append(group_length)
        count += 1

        # Going to next index
        group1, group2, group3, group4 = least_load_sort_index(index, count, groups)
        break

    return group1, group2, group3, group4

    group1, group2, group3, group4 = least_load_sort_index(index_fasta(path2fsa), count, groups)
"""
################################## EXECUTION ###################################
start_time = time.time()
kmer_dict = dict()

jobs = index_fasta(path2fsa)

a_total = 0
t_total = 0
g_total = 0
c_total = 0
count = 0

#main_time = time.time()
if __name__ == '__main__':
    jobs = jobs
    result = Parallel(n_jobs = 8)(delayed(kmer_fun)(path2fsa, idx, kmer_dict) for idx in jobs)
    for res in result:
        a_total += res[1]
        t_total += res[2]
        g_total += res[3]
        c_total += res[4]

        # Merging dicts
        kmer_dict = {key: kmer_dict.get(key, 0) + res[0].get(key, 0) for key in res[0]}

    with open("kmer_overrepresentation.txt", "w") as fo:
        seq_len = a_total + t_total + g_total + c_total
        P_a = a_total/seq_len
        P_t = t_total/seq_len
        P_g = g_total/seq_len
        P_c = c_total/seq_len
        for kmer in kmer_dict.keys():
            P_n = list()
            for i in range(len(kmer)):
                if kmer[i] == "a":
                    P_n.append(P_a)
                if kmer[i] == "t":
                    P_n.append(P_t)
                if kmer[i] == "g":
                    P_n.append(P_g)
                if kmer[i] == "c":
                    P_n.append(P_c)

            # Calculating P(kmer)
            P_kmer = math.prod(P_n)

            if kmer_dict[kmer]/len(kmer_dict) > P_kmer:
                count += 1
                b = round(kmer_dict[kmer]/len(kmer_dict),7)
                fo.write(f"{kmer}: \t  {b} >  {P_kmer} \n")
print("Time:", time.time()-start_time)
