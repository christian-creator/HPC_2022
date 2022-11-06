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

# Read fasta file and split into separate files, it returns a list of filenames, for the files it has generated.
def split_fasta(path):
    tmp_filenames = list()
    file_count = 1
    with open(path, "rb") as fi:
        not_first = False
        for line in fi:
            if line.startswith(b">"):
                if not_first:
                    tf.close()
                    file_count += 1
                    tf = open(f"{file_count}.fasta_sequence_temp.fsa", "wb")
                    tmp_filenames.append(f"{file_count}.fasta_sequence_temp.fsa")
                    tf.write(line)
                else:
                    tf = open(f"{file_count}.fasta_sequence_temp.fsa", "wb")
                    tmp_filenames.append(f"{file_count}.fasta_sequence_temp.fsa")
                    tf.write(line)
                    not_first = True
            else:
                tf.write(line)

    return tmp_filenames

# Function for counting bases in the entry_line
def bases_count (entry_line):
    A_count = entry_line.count("a")
    T_count = entry_line.count("t")
    C_count = entry_line.count("c")
    G_count = entry_line.count("g")
    N_count = entry_line.count("n")

    return A_count, T_count, C_count, G_count, N_count

# Worker function that results in the reverse complement of the sequence
def reverse_complement(filename, translationTable):
    # Initialise variables
    com_DNA = ""
    rev_DNA = ""

    with open(filename, "r") as fi:
        for line in fi:
            if line.startswith(">"):
                header = line[:-1]
            else:
                com_DNA += line

    # Complementing the string
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

filename_collecter = split_fasta(path2fsa)

if __name__ == '__main__':
    jobs = filename_collecter
    result = Parallel(n_jobs=4)(delayed(reverse_complement)(x, translationTable) for x in jobs)
    for res in result:
        with open("reverse_human.fsa", "w") as fo:
            for res in result:
                fo.write(res)

################################## CLEAN-UP ####################################

for file in filename_collecter:
    os.remove(file)

print("Time:", time.time()-start_time)
