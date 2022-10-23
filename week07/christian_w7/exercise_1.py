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
                        help="The fasta-file to index")
    
    parser.add_argument("-index", "--index_file", type=str, dest="indexfile",
                        metavar="PATH",
                        help="The output index file")
    
    return parser


def get_args():
    parser = get_parser()
    args = parser.parse_args()
    return args



def Indexer(path_infile, index_file):
    index_file = open(index_file, "w+")  
    byte_tracker = 0
    header_start = None
    header_end = None
    seq_start = None
    seq_end = None
    with open(path_infile, "rb") as infile:
        for line in infile:
            if line.startswith(b">"):
                if seq_end is not None:
                    print(f"{header_start} {header_end} {seq_start} {seq_end}",file=index_file)
                header_start = byte_tracker
                header_end = byte_tracker + len(line) - 1
                seq_start = header_end + 1 
                seq_end =  header_end
            else:
                seq_end += len(line)
            byte_tracker += len(line)
        else:
            print(f"{header_start} {header_end} {seq_start} {seq_end}",file=index_file) 
    

def main(args):
    # put your code here
    Indexer(args.infile, args.indexfile)


if __name__ == "__main__":
    start_time = datetime.now()
    args = get_args()
    main(args)
    end_time = datetime.now()
