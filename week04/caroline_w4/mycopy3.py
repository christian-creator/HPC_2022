#!/usr/bin/env python3

infile_path = "/home/projects/pr_course/human.fsa"
outfile_path = "/home/projects/pr_course/people/carmar/week04/human.fsa"

infile = open(infile_path, "rb")
outfile = open(outfile_path, "wb")

for line in infile:
    outfile.write(line)

infile.close()
outfile.close()

