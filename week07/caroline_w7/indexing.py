#!/usr/bin/env python3

"""
real	0m10.766s
user	0m8.722s
sys	0m1.241s
"""
# Files
infile_path = "/home/projects/pr_course/human.fsa"
fasta_infile = open(infile_path, "rb")

outfile_path = "/home/projects/pr_course/people/carmar/week07/index_humanfsa.txt"
index_file = open(outfile_path, "w")

# Flag
not_first = False

# Indexing the file
for line in fasta_infile:
        if not_first:
                if line.startswith(b">"):
                        seq_end = fasta_infile.tell() - len(line) - 1
                        seq_start = fasta_infile.tell()
                        header_start = seq_start - len(line)
                        header_end =  seq_start - 1
                        index_file.write(str(seq_end) + "\n" + str(header_start) + " " +  str(header_end) +" " + str(seq_start) + " " )
                else:
                        continue
        else:
                seq_start = fasta_infile.tell()
                header_start = seq_start - len(line)
                header_end =  seq_start - 1
                index_file.write(str(header_start) + " " + str(header_end) + " " + str(seq_start) + " " )

        not_first = True

seq_end = fasta_infile.tell()
index_file.write(str(seq_end) + "\n")

# Closing files
fasta_infile.close()
index_file.close()
