import sys
import os
import argparse
from datetime import datetime

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

def count_bases(entry):
    N_counts = entry.count("n")
    A_counts = entry.count("a")
    T_counts = entry.count("t")
    G_counts = entry.count("g")
    C_counts = entry.count("c")
    return f"A:{A_counts} T:{T_counts} C:{C_counts} G:{G_counts} N:{N_counts}"




def get_complement_strands(infile_path,outfile_path):
    outfile = open(outfile_path,"w")
    with open(infile_path,"r") as f:
        entry = ""
        for line in f:
            if line[0] == ">":
                if len(entry) > 0:
                    translation_table = entry.maketrans("atgc","tacg")
                    base_counts = count_bases(entry)
                    print(header + " " + base_counts, file=outfile)
                    print(entry.translate(translation_table),file=outfile)
                header = line.rstrip()
                entry = ""

            else:
                entry += line

        else:
            # Writing last entry
            translation_table = entry.maketrans("atgc","tacg")
            base_counts = count_bases(entry)
            print(header + " " + base_counts, file=outfile)
            print(entry.translate(translation_table),file=outfile)
    outfile.close()

def main(args):
    # put your code here
    get_complement_strands(args.infile, args.outfile)

if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Begin at {start_time}")
    args = get_args()
    print("# args:", args)
    main(args)
    end_time = datetime.now()
    print("# Done!")
    print(f"# Duration: {end_time - start_time}")
