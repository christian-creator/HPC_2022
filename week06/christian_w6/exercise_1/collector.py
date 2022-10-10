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
    parser.add_argument("-in", "--translated", type=str, dest="translated",
                        metavar="DIR",
                        help="The directory cotaining translated sequences")

    parser.add_argument("-o", "--outfile", type=str, dest="outfile",
                        metavar="PATH",
                        help="The tmp directory for single fasta files")
    
    return parser


def get_args():
    parser = get_parser()
    args = parser.parse_args()
    return args


def Collector(path_translated,path_outfile):
    sorted_infiles = sorted(os.listdir(path_translated), key = lambda x: int(x.split("_")[2]))
    outfile = open(path_outfile, "wb") 
    for file_ in sorted(os.listdir(path_translated)):
        path_to_file = os.path.join(path_translated,file_)
        rev_complement_file = open(path_to_file, 'rb')
        for line in rev_complement_file:
            outfile.write(line)
        rev_complement_file.close() 
    outfile.close()
    

def main(args):
    # put your code here
    Collector(args.translated, args.outfile)


args = get_args()
main(args)
