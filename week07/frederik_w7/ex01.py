#!/usr/bin/env python3

import sys

filename = sys.argv[1]

outfilename = filename.rsplit(".", 1)[0] + ".idx"

count = 0

idx = []

with open(filename, "r") as f:
    for line in f:
        if line.startswith(">"):
            if idx:
                idx[len(idx) - 1][3] = count - 1 
            idx.append([count, count + len(line), count + len(line) + 1, None])
        count += len(line)

idx[len(idx) - 1][3] = count - 1

with open(outfilename, "w") as f:
    for entry in idx:
        print("\t".join([str(x) for x in entry]), file=f)

