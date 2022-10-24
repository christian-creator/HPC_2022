#!/usr/bin/env python3

import sys
import time

filename = sys.argv[1]
outfilename = filename.rsplit(".", 1)[0] + ".idx"

idx = []
start = time.perf_counter()

# Would be much faster with chunk reading and find(">")
# but requires a complete rewrite and logic rethink
# which I cannot get myself to do. Whoops.

with open(filename, "rb") as f:
    line = f.readline()
    while line:
        if line.startswith(b">"):
            pos = f.tell()
            if idx:
                idx[len(idx) - 1][3] = pos - len(line) - 1
            idx.append([pos - len(line), pos, pos + 1, None])
        line = f.readline()
    idx[len(idx) - 1][3] = f.tell()

with open(outfilename, "w") as f:
    for entry in idx:
        print("\t".join([str(x) for x in entry]), file=f)

end = time.perf_counter()

print("Runtime:", end-start, "seconds")

