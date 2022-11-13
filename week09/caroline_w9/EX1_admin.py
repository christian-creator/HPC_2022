#!/usr/bin/env python3

################################### PACKAGES ###################################

import subprocess
import os
import time
from joblib import Parallel, delayed

#################################### INPUT #####################################

path2fsa = "human.fsa"

################################## FUNCTIONS ###################################

def split_fasta(path):
    header_seq = list()
    with open(path, "r") as fi:
        header = None
        seq = list()
        for line in fi:
            if line.startswith(">"):
                if header != None:
                    seq_print = "".join(seq)
                    header_seq.append(f"{header}, {seq_print}")
                header = line[:-1]
            else:
                seq.append(line)
        if header != None:
            seq_print = "".join(seq)
            header_seq.append(f"{header}, {seq_print}")

    return header_seq

# Function for counting bases in the entry_line
def bases_count (entry_line):
    A_count = entry_line.count("a")
    T_count = entry_line.count("t")
    C_count = entry_line.count("c")
    G_count = entry_line.count("g")
    N_count = entry_line.count("n")

    return A_count, T_count, C_count, G_count, N_count

# Worker function that results in the reverse complement of the sequence
def reverse_complement(header_seq):
    # Initialise variables
    rev_DNA = ""

    #
    header, com_DNA = header_seq.split(",")

    # Complementing the string
    translationTable = str.maketrans("atcg","tagc")
    com_DNA = com_DNA.translate(translationTable)

    # Counting bases in complement string
    A_count, T_count, C_count, G_count, N_count = bases_count(com_DNA)

    # Reversing the string
    for i in range(1,len(com_DNA)):
        rev_DNA += com_DNA[-(i+1)]

    # Preparing for Printing
    header_sequence = header + f" (A: {A_count}, T: {T_count}, C: {C_count} G: {G_count} Other: {N_count}) \n" + rev_DNA + "\n"

    return header_sequence

################################## EXECUTION ###################################

start_time = time.time()

#header_seq = split_fasta(path2fsa)


if __name__ == '__main__':
    result = Parallel(n_jobs=2)(delayed(reverse_complement)(header_seq) for header_seq in split_fasta(path2fsa))
    for res in result:
        with open("reverse_human.fsa", "w") as fo:
            for res in result:
                fo.write(res)

print("Time:", time.time()-start_time)
