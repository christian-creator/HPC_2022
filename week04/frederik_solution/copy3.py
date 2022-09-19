#!/usr/bin/env python3

infile_path = "/home/projects/pr_course/human.fsa"
outfile_path = "/home/projects/pr_course/people/fregad/human.fsa"

with open(outfile_path, "wb") as outfile, open(infile_path, "rb") as infile:
    for line in infile:
        outfile.write(line)

