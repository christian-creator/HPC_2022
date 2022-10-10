import sys
import os
import argparse
from datetime import datetime
import subprocess


def get_parser():
    # Build commandline parser
    parser = argparse.ArgumentParser(
        description="Description of what the script does")
    # Arguments
    parser.add_argument("-i", "--infile", type=str, dest="infile",
                        metavar="FILE",
                        help="The inputfile to calculate complement strads")
    
    parser.add_argument("-o", "--outfile", type=str, dest="outfile",
                        metavar="PATH",
                        help="The output file of reverse complement strand")
    return parser


def get_args():
    parser = get_parser()
    args = parser.parse_args()
    return args


def read_fasta(fp):
    name, seq = None, []
    for line in fp:
        line = line.rstrip()
        if line.startswith(">"):
            if name: yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)
    if name: yield (name, ''.join(seq))

def count_bases(entry):
    N_counts = entry.count("n")
    A_counts = entry.count("a")
    T_counts = entry.count("t")
    G_counts = entry.count("g")
    C_counts = entry.count("c")
    return f"A:{A_counts} T:{T_counts} C:{C_counts} G:{G_counts} N:{N_counts}"


def Worker(path_infile,path_outfile):
    outfile = open(path_outfile,"w+")
    with open(path_infile) as fp:
        for name, seq in read_fasta(fp):
            # Calculating reverse complement
            seq = seq[::-1] # Reverse the sequence 
            translation_table = seq.maketrans("atgc","tacg")
            translated = seq.translate(translation_table)
            # Calculate number of bases
            base_counts = count_bases(translated)
            # Format sequence for output
            window_size = 60
            formatted = [translated[i:i+window_size] for i in range(0, len(translated),window_size)]
            print(name + " " + base_counts, file=outfile)
            print("\n".join(formatted), file=outfile)
    outfile.close()      

def main(args):
    # put your code here
    Worker(args.infile,args.outfile)


args = get_args()
main(args)
