"""
    Runtime: 155.63s user 0.55s system 99% cpu 2:36.73 total for Human Chromosome 1
"""

import sys
import os
import argparse
from datetime import datetime
import subprocess
import time
import subprocess



def get_parser():
    # Build commandline parser
    parser = argparse.ArgumentParser(
        description="Description of what the script does")
    # Arguments
    parser.add_argument("-in", "--infile", type=str, dest="infile",
                        metavar="FILE",
                        help="The inputfile to calculate complement strads")
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


def generate_kmers(input_string,kmer_lengths):
    """Generator used to create all possible K-mers from the sequence with the
       specified lengths. 


    Args:
        input_string (str): The chromosome sequence
        kmer_lengths (list): The kmer lengths

    Yields:
        str: Kmer
    """
    for i in range(len(input_string)-min(kmer_lengths)):
        for length in kmer_lengths:
            yield (input_string[i:i+length],length)

def get_kmer_dict_basecounts(infile):
    basecounts = {"a":0,"t":0,"g":0,"c":0}
    kmer_lengths = [5,6,7] # 5,6,7
    all_kmers = {length:{} for length in kmer_lengths}

    with open(infile,"r") as infile:
        for name, seq in read_fasta(infile):
            # sample_size = int(248956422/100)
            # seq = seq[:sample_size]
            # Counting the bases
            basecounts["a"] += seq.count("a")
            basecounts["t"] += seq.count("t")
            basecounts["g"] += seq.count("g")
            basecounts["c"] += seq.count("c")

            for kmer,length in generate_kmers(seq,kmer_lengths):
                if kmer not in all_kmers[length]:
                    all_kmers[length][kmer] = 1
                else:
                    all_kmers[length][kmer] += 1

    basecounts = {nc:count/sum(basecounts.values()) for nc,count in basecounts.items()}
    return all_kmers, basecounts

def calculate_product(list):
    product = list[0]
    for num in list[1:]:
        product *= num
    return product

def find_overrepresented_kmers(all_kmers,basefreqs):
    for length in all_kmers.keys():
        print(f"{length:#^20}")
        num_kmers = sum(all_kmers[length].values())
        for kmer in all_kmers[length].keys():
            if 1 in [nuc not in 'acgt' for nuc in kmer]:
                prior = calculate_product([basefreqs[nc] for nc in kmer])
                if all_kmers[length][kmer]/num_kmers > prior:
                    print(kmer, all_kmers[length][kmer], num_kmers, all_kmers[length][kmer]/num_kmers, prior)

def main(args): 
    all_kmers, basecounts = get_kmer_dict_basecounts(args.infile)
    find_overrepresented_kmers(all_kmers, basecounts)


if __name__ == "__main__":
    start_time = datetime.now()
    args = get_args()
    main(args)
    end_time = datetime.now()


