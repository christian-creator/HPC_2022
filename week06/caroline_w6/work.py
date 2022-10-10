#!/usr/bin/env python3

from argparse import ArgumentParser

# Argument Parser
parser = ArgumentParser(description="Reverse Complement of inputted DNA sequence")
parser.add_argument("-f", action="store", dest="filename", type=str, help="filenames")

args = parser.parse_args()
filename = args.filename

# Opening files
infile = open(filename, "r")
outfile = open("output_{}".format(filename), "w")

# Initialise helper functions and variables
translationTable = str.maketrans("atcg","tagc")
com_DNA = ""
rev_DNA = ""
header = ""

# Function for counting bases in the entry_line
def bases_count (entry_line):
    A_count = entry_line.count("a")
    T_count = entry_line.count("t")
    C_count = entry_line.count("c")
    G_count = entry_line.count("g")
    N_count = entry_line.count("n")

    return A_count, T_count, C_count, G_count, N_count

# Main script
with open(filename,"r") as fi:
    for line in infile:
        if line.startswith(">"):
            header = line.replace("\n", "")
        else:
            com_DNA += line
    # Printing
    outfile.write(header)
    A_count, T_count, C_count, G_count, N_count = bases_count(com_DNA)
    outfile.write(" (A: %i, T: %i, C: %i G: %i Other: %i) \n" % (A_count, T_count, C_count, G_count, N_count))
    # Complementing the sequence
    com_DNA = com_DNA.translate(translationTable)
    # Reversing the strand
    for i in range(1,len(com_DNA)):
        rev_DNA += com_DNA[-(i+1)]
    outfile.write(rev_DNA + "\n")

# closing files
outfile.close()

