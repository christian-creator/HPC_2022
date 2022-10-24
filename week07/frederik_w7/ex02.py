#!/usr/bin/env python3

import sys

filename = sys.argv[1]
n_entry = int(sys.argv[2])

idxname = filename.rsplit(".", 1)[0] + ".idx"



with open(idxname, "r") as f:
    idx = [[int(y) for y in x.strip().split("\t")] for x in f.readlines()]
    header_start, header_end, seq_start, seq_end = idx[n_entry]


with open(filename, "r") as f:
    f.seek(header_start)
    header = f.read(header_end - header_start).strip()
    print(header)
    seq = f.read(seq_end - seq_start + 1)
    print(seq)


