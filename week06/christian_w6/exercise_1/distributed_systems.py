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
    parser.add_argument("-in", "--infile", type=str, dest="infile",
                        metavar="FILE",
                        help="The inputfile to calculate complement strads")
    
    parser.add_argument("-o", "--outfile", type=str, dest="outfile",
                        metavar="FILE",
                        help="The outputfile of the reverse complement")
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


def Worker(path_to_file):
    ...


def Administrator(infile):
    with open(infile) as fp:
        outfile_counter = 0 
        for name, seq in read_fasta(fp):
            outfile = open(f"tmp/fasta_entry_{outfile_counter}.fa","w+")
            outfile.write(name + "\n" + seq)
            outfile_counter += 1
    


def main(args):
    # put your code here
    job = subprocess.run(['mkdir', 'tmp/'])
    Administrator(args.infile)


if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Begin at {start_time}")
    args = get_args()
    print("# args:", args)
    main(args)
    end_time = datetime.now()
    print("# Done!")
    print(f"# Duration: {end_time - start_time}")
