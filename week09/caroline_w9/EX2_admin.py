#!/usr/bin/env python3

################################### PACKAGES ###################################

import subprocess
import os
import time
from joblib import Parallel, delayed

translationTable = str.maketrans("atcg","tagc")

#################################### INPUT #####################################

path2fsa = "human.fsa"

################################## FUNCTIONS ###################################

# Read fasta file and indexes it.
def index_fasta(path):
    # Flag
    not_first = False
    index = list()

    with open(path, "rb") as fi:
        # Indexing the file
        for line in fi:
            if not_first:
                if line.startswith(b">"):
                    seq_end = fi.tell() - 1
                    index.append(str(header_start) + " " +  str(header_end) + " " + str(seq_start) + " " + str(seq_end))
                    seq_start = fi.tell()
                    header_end = seq_start - 1
                    header_start = seq_start - len(line)
                else:
                    continue
            else:
                seq_start = fi.tell()
                header_start = seq_start - len(line)
                header_end =  seq_start - 1
                not_first = True

        seq_end = fi.tell()
        index.append(str(header_start) + " " +  str(header_end) + " " + str(seq_start) + " " + str(seq_end))

    return index

# Function for counting bases in the entry_line
def bases_count (entry_line):
    A_count = entry_line.count("a")
    T_count = entry_line.count("t")
    C_count = entry_line.count("c")
    G_count = entry_line.count("g")
    N_count = entry_line.count("n")

    return A_count, T_count, C_count, G_count, N_count

# Worker function that results in the reverse complement of the sequence
def reverse_complement(filename, idx):
    # Initialise variables
    com_DNA = ""
    rev_DNA = ""
    header_start, header_end, seq_start, seq_end = idx.split()

    with open(filename, "r") as fi:
        # Finding the header and sequence from the index
        fi.seek(int(header_start))
        header = fi.read(int(header_end) - int(header_start))
        com_DNA = fi.read(int(seq_end) - int(seq_start))


    # Complementing the string
    com_DNA = com_DNA.translate(translationTable)

    # Counting bases in complement string
    A_count, T_count, C_count, G_count, N_count = bases_count(com_DNA)

    # Reversing the string
    for i in range(1,len(com_DNA)):
        rev_DNA += com_DNA[-(i+1)]

    # Printing
    with open(f"{header_start}_rev_com.txt", "w") as fo:
        fo.write(header + f" (A: {A_count}, T: {T_count}, C: {C_count} G: {G_count} Other: {N_count}) \n" + rev_DNA[:-1] + "\n")

    return f"{header_start}_rev_com.txt"

################################## EXECUTION ###################################

start_time = time.time()

# Getting index from input .fsa
index = index_fasta(path2fsa)

print("Indexing done in:", time.time()-start_time)

# MAIN
if __name__ == '__main__':
    jobs = index
    result = Parallel(n_jobs=8)(delayed(reverse_complement)(path2fsa, x) for x in jobs)
    with open("reverse_human.fsa", "w") as fo:
        for res in result:
            tmp_file = "".join(res)
            # Copying content from temporary files into main outfile
            with open(tmp_file, "r") as tmp_fi:
                while True:
                    chunk = tmp_fi.read(10000)
                    fo.write(chunk)
                    if len(chunk) < 10000:
                        break

################################## CLEAN-UP ####################################

for file in result:
    os.remove(file)

print("Time:", time.time()-start_time)
