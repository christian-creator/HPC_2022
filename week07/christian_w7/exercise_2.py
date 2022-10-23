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
    parser.add_argument("-if", "--fastafile", type=str, dest="fastafile",
                        metavar="FILE",
                        help="The inputfile to calculate complement strads")
    
    parser.add_argument("-cor", "--coordinates", type=str, dest="cords",
                        metavar="HEADER_START HEADEREND SEQSTART SEQEND",
                        help="The coordinates of the entry")
    
    return parser


def get_args():
    parser = get_parser()
    args = parser.parse_args()
    return args



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
    print(str(header))
    print(str(seq)) 


def main(args):
    # put your code here
    Reader(args.fastafile, args.cords)


if __name__ == "__main__":
    start_time = datetime.now()
    args = get_args()
    main(args)
    end_time = datetime.now()
