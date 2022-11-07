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
    
    parser.add_argument("-tmp", "--tmp_dir", type=str, dest="tmp_dir",
                        metavar="PATH",
                        help="The tmp directory for single fasta files")
     
    parser.add_argument("-out", "--out_file", type=str, dest="out_file",
                        metavar="PATH",
                        help="The final output file with collected fastas")
    return parser


def get_args():
    parser = get_parser()
    args = parser.parse_args()
    return args



def syscall(command):
    job = subprocess.run(command.split(),
          stdout=subprocess.PIPE, universal_newlines=True)
    result = job.stdout
    return result



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

# Functions for the indexing
def find_all(a_str, pattern):
    start = 0
    while True:
        start = a_str.find(pattern, start)
        if start == -1:
            return
        yield start
        start += len(pattern)  # use start += 1 to find overlapping matches

def Indexer(path_infile, index_file):
    """The optimized Indexer reads the fasta file in chunks and instead of iterating over the chunks it looks for the header start ">" 
       and then calculates every entry postion relative to the header starts. I found that this solution was roughly 10x faster than the 
       solution from exercise 1. 
       !!!
       I found that this indexer could index the entire human.fsa file in 0.78 seconds and have the same indexes as the slower solution.
       However, the time seem to vary based on the node on computerome. 
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

# Functions for translating and counting bases
def Reader(path_infile, coordinates):
    h_start, h_end, seq_start, seq_end = [int(x) for x in coordinates.split()]
    fastafile = open(path_infile, 'rb')
    header_len = h_end - h_start
    seq_len = seq_end - seq_start
    
    # Print Header
    fastafile.seek(h_start)
    header = fastafile.read(header_len)
    # Print SEQ
    fastafile.seek(seq_start)
    seq = fastafile.read(seq_len)
    fastafile.close()
    seq = seq.replace(b"\n",b"")
    return header, seq

def count_bases(entry):
    N_counts = entry.count(b"n")
    A_counts = entry.count(b"a")
    T_counts = entry.count(b"t")
    G_counts = entry.count(b"g")
    C_counts = entry.count(b"c")
    return f"A:{A_counts} T:{T_counts} C:{C_counts} G:{G_counts} N:{N_counts}\n".encode(encoding='ascii')


def Worker(path_infile, coordinates):
    name, seq = Reader(path_infile, coordinates)
    # Calculating reverse complement
    seq = seq[::-1] # Reverse the sequence 
    translation_table = seq.maketrans(b"atgc",b"tacg")
    translated = seq.translate(translation_table)
    # Calculate number of bases
    base_counts = count_bases(translated)
    # Format sequence for output
    window_size = 60
    formatted = [translated[i:i+window_size] for i in range(0, len(translated),window_size)]
    
    new_header =  name + b" " + base_counts
    rev_comp_seq = b"\n".join(formatted)

    return new_header,rev_comp_seq


# FUnction for the Administrator
def Administrator_collector(infile,index_file,out_file):
    with open(index_file) as indexfile:
        all_coordinates = [] 
        for coordinates in indexfile:
            all_coordinates.append((coordinates.rstrip()))

    result = Parallel(n_jobs=4)(delayed(Worker)(infile,coordinate) for coordinate in all_coordinates)
    
    # I was unaable to find an intelligent strategy to write directly to the file.
    # Instead i save the entire translated seq in memory in the result object and then write this object directly to the input file.
    # To make the solution more intelligent it would be cool to make the worker able to write the output directly to the input fasta after it has translated and reversed.
    # Here i think that the following solutions are useful:
        # 1. The sequences of the unout and output sequences are of equal length and the only difference is the header size
        # 2. Using the .seek() funciton we can write to specific lines.
    # Still i was unable to figure out a strategy to do this while multiple workers are in the same file. If worker 1 is done before Worker 8 has begun reading the file then the
    # indexes are wrong. 
    with open(infile, "wb") as outfile:
        for header,translated in result:
            outfile.write(header)
            outfile.write(translated)



def main(args): 
    # Indexing the fasta file
    index_filename = "index.txt"
    Indexer2(args.infile, index_filename)
    # Reading the index and passing coordinates to the Workers
    Administrator_collector(args.infile, index_filename, args.out_file)
    # Wait for all tmp files to be removed in worker. When empty all files have been translated 

if __name__ == "__main__":
    start_time = datetime.now()
    args = get_args()
    main(args)
    end_time = datetime.now()
