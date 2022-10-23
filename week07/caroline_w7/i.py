#!/usr/bin/env python3

"""
Time:
real	0m8.050s
user	0m7.396s
sys	0m0.478s
"""
# Files
infile_path = "/home/projects/pr_course/human.fsa"
outfile_path = "/home/projects/pr_course/people/carmar/week07/index_humanfsa.txt"

# Flag
first = False

# Indexing the file
with open(infile_path, "rb") as fasta_infile:
    for line in fasta_infile:
            if first:
                    if line.startswith(b">"):
                            line_length = len(line)
                            seq_start = fasta_infile.tell()
                            open(outfile_path, "w").write(str(seq_start - line_length - 1) + "\n" + str(seq_start - line_length) + " " +  str(seq_start - 1) +" " + str(seq_start) + " " )
                    else:
                            continue
            else:
                    line_length = len(line)
                    seq_start = fasta_infile.tell()
                    open(outfile_path, "w").write(str(seq_start - line_length) + " " + str(seq_start - 1) + " " + str(seq_start) + " " )

            first = True

    seq_end = fasta_infile.tell()
    open(outfile_path, "w").write(str(seq_end) + "\n")
