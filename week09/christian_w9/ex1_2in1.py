import sys
import os
import argparse
from datetime import datetime
import subprocess
import time
from joblib import Parallel, delayed
import subprocess



def get_parser():
    # Build commandline parser
    parser = argparse.ArgumentParser(
        description="Description of what the script does")
    # Arguments
    parser.add_argument("-in", "--infile", type=str, dest="infile",
                        metavar="FILE",
                        help="The inputfile to calculate complement strads")
     
    parser.add_argument("-out", "--out_file", type=str, dest="out_file",
                        metavar="PATH",
                        help="The final output file with collected fastas")
    return parser


def get_args():
    parser = get_parser()
    args = parser.parse_args()
    return args

def count_bases(entry):
    N_counts = entry.count("n")
    A_counts = entry.count("a")
    T_counts = entry.count("t")
    G_counts = entry.count("g")
    C_counts = entry.count("c")
    return f"A:{A_counts} T:{T_counts} C:{C_counts} G:{G_counts} N:{N_counts}"


def Worker(name,seq):
    """ Input is the header and sequence from a fasta entry, while the output is a modified header and the reverse complement seq"""
    
    # Calculating reverse complement
    seq = seq[::-1] # Reverse the sequence 
    translation_table = seq.maketrans("atgc","tacg")
    translated = seq.translate(translation_table)
    # Calculate number of bases
    base_counts = count_bases(translated)
    # Format sequence for output
    window_size = 60
    formatted = [translated[i:i+window_size] for i in range(0, len(translated),window_size)]
    return (name + " " + base_counts, "\n".join(formatted))


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


def Administrator_collector(infile, out_file):
    with open(infile) as fp: 
        jobs = [] 
        for counter,(name, seq) in enumerate(read_fasta(fp)):
            jobs.append((name,seq)) 

    # Call the worker on the passed name and seq
    result = Parallel(n_jobs=4)(delayed(Worker)(name, seq) for name,seq in jobs)

    # Writing the output to the file
    with open(out_file, "w+") as outfile:
        for name,entry in result:
            print(name,file=outfile)
            print(entry,file=outfile)



def main(args):
    Administrator_collector(args.infile, args.out_file)

if __name__ == "__main__":
    start_time = datetime.now()
    args = get_args()
    main(args)
    end_time = datetime.now()
