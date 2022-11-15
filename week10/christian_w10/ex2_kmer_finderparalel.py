import sys
import os
import argparse
from datetime import datetime
import subprocess
import time
import subprocess
from joblib import Parallel, delayed


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


# Functions for the indexing
def find_all(a_str, pattern):
    start = 0
    while True:
        start = a_str.find(pattern, start)
        if start == -1:
            return
        yield start
        start += len(pattern)  # use start += 1 to find overlapping matches

def Indexer2(path_infile, index_file):
    """The optimized Indexer reads the fasta file in chunks and instead of iterating over the chunks it looks for the header start ">" 
       and then calculates every entry postion relative to the header starts.
    Args:
        path_infile (str): path to fasta-file it should index
        index_file (str): path to the output index file
    """
    index_file = open(index_file, "w+")
    # For timing the indexers
    start = time.time()
    # Miscellaneous variables for indexing
    first_header = True
    tracker = 0 # The tracker is used to track what chunk we are in with the number of bytes in each chunk
    with open(path_infile, "rb") as infile:
        while True:
            chunk = infile.read(100000)
            # Finds all ">" in the chunk and gives the byte position
            all_headers = list(find_all(chunk, b">"))
            # There can more than 1 header in a chunk therefore i iterate over a list
            if len(all_headers) > 0:
                for header_index in all_headers:
                    # The header position + what "chunk" we are in indicated by the tracker
                    header = header_index + tracker
                    # The end of the header is found by looking for the next newline.
                    end_header = chunk[header_index:].find(b"\n") + header
                    
                    # Here i just use a cheap trick for the right format.
                    if first_header is True:
                        index_file.write(
                            f"{header} {end_header} {end_header + 1} ")
                        first_header = False
                    else:
                        index_file.write(
                            f" {header - 1}\n{header} {end_header} {end_header + 1}")

            tracker += len(chunk)
            if len(chunk) < 100000:
                # When done i know that the last line is the sequence end of the last entry. 
                index_file.write(f" {tracker}\n")
                break

    index_file.close()
    end = time.time()
    print(f"Indexer2 Runtime of the indexing is: {end - start}")


def Reader(path_infile, coordinates):
    """ Reads and index coordinates and returns the header and the seq"""
    
    h_start, h_end, seq_start, seq_end = [int(x) for x in coordinates.split()]

    with open(path_infile, "rb") as f:
        # get header and sequence
        f.seek(int(h_start))
        header = f.read(int(h_end) - int(h_start)+1)
        f.seek(int(seq_start))
        seq_str = f.read(int(seq_end) - int(seq_start)+1)
    
    seq_str = seq_str.replace(b"\n",b"")
    seq_str = seq_str.decode("utf-8")
    return header, seq_str

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

def get_kmer_dict_basecounts(path_infile,index,kmer_lengths):
    """Retrieve the K-mer counts and base-counts given an index of an entry in the the chromosome fasta-file.
       

    Args:
        path_infile (str): Path to fasta-file
        index (str): Path to indexed fasta-file
        kmer_lengths (list): The k-mer lengths

    Returns:
        dict,dict: K-mer counts, Base-counts
    """
    name, seq = Reader(path_infile,index)
    # Intializing the k-mer dict
    all_kmers = {length:{} for length in kmer_lengths}
    base_counts = {"a":0,"t":0,"g":0,"c":0}

    # Counting the bases
    base_counts["a"] += seq.count("a")
    base_counts["t"] += seq.count("t")
    base_counts["g"] += seq.count("g")
    base_counts["c"] += seq.count("c")

    # Counting the k-mers by itertating over generator K-mers.
    for kmer,length in generate_kmers(seq,kmer_lengths):
        if kmer not in all_kmers[length]:
            all_kmers[length][kmer] = 1
        else:
            all_kmers[length][kmer] += 1

    return all_kmers, base_counts

def calculate_product(list):
    """Calculate product of list. Used to calculate the product of base-frequencies.

    Args:
        list (list): Base frequencies

    Returns:
        float: Porduct of base-frquencies 
    """
    product = list[0]
    for num in list[1:]:
        product *= num
    return product

def find_overrepresented_kmers(all_kmers,basefreqs):
    """Calcualtes and prints the overrepresented kmers based on the following in-equality:
       count(atgca-mers)/count(5-mers) > P(a)*P(t)*P(g)*P(c)*P(a)

    Args:
        all_kmers (dict): K-mer counts
        basefreqs (dict): Base frequencies
    """
    for length in all_kmers.keys():
        print(f"{length:#^20}")
        num_kmers = sum(all_kmers[length].values())
        for kmer in all_kmers[length].keys():
            # Only print the K-mer if it only contains atgc
            if True not in [nuc not in 'atgc' for nuc in kmer]:
                # Calculating equivelant to ~P(a)*P(t)*P(g)*P(c)*P(a)
                prior = calculate_product([basefreqs[nc] for nc in kmer])
                # If significant
                if all_kmers[length][kmer]/num_kmers > prior:
                    print(kmer, all_kmers[length][kmer], num_kmers, all_kmers[length][kmer]/num_kmers, prior)


def Administrator(path_infile,index_file):
    """Run get_kmer.. for each chromosome 

    Args:
        path_infile (_type_): _description_
        index_file (_type_): _description_

    Returns:
        _type_: _description_
    """
    kmer_lengths = [5,6,7] # 5,6,7
    # Load-balancing is acheived by sorting the indexes by the number of bytes thus acheiving Least-Load.
    coordinates = sorted([index.rstrip() for index in open(index_file,"r").readlines()], 
                            key=lambda x: int(x.split()[-1]) - int(x.split()[-2]),
                            reverse=True) 


    result = Parallel(n_jobs=7)(delayed(get_kmer_dict_basecounts)(path_infile, coord,kmer_lengths) for coord in coordinates)

    all_kmers = {length:{} for length in kmer_lengths}
    all_basecounts = {"a":0,"t":0,"g":0,"c":0}


    for d,count in result:
        for length in kmer_lengths:
            for kmer,occ in d[length].items():
                if kmer not in all_kmers:
                    all_kmers[length][kmer] = occ
                else:
                    all_kmers[length][kmer] += occ

        all_basecounts["a"] += count["a"]
        all_basecounts["t"] += count["t"]
        all_basecounts["g"] += count["g"]
        all_basecounts["c"] += count["c"]

    all_basecounts = {nc:count/sum(all_basecounts.values()) for nc,count in all_basecounts.items()}
    return all_kmers,all_basecounts



def main(args): 
    index_file = "index.txt"
    Indexer2(args.infile, index_file)
    all_kmers, base_counts = Administrator(args.infile,index_file)
    find_overrepresented_kmers(all_kmers, base_counts)


if __name__ == "__main__":
    start_time = datetime.now()
    args = get_args()
    main(args)
    end_time = datetime.now()