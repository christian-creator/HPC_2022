import sys
import os
import argparse
from datetime import datetime
import subprocess
import time
import re


def get_parser():
    # Build commandline parser
    parser = argparse.ArgumentParser(
        description="Description of what the script does")
    # Arguments
    parser.add_argument("-i", "--infile", type=str, dest="infile",
                        metavar="FILE",
                        help="The inputfile to calculate complement strads")

    parser.add_argument("-index", "--index_file", type=str, dest="indexfile",
                        metavar="PATH",
                        help="The tmp directory for single fasta files")

    return parser


def get_args():
    parser = get_parser()
    args = parser.parse_args()
    return args


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


def main(args):
    Indexer2(args.infile, args.indexfile)


if __name__ == "__main__":
    args = get_args()
    main(args)
