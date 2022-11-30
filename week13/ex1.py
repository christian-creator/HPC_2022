#!/usr/bin/env python3

import sys
import gzip

if len(sys.argv) != 2:
    print("Supply just one argument, file.")
    sys.exit(1)

fqname = sys.argv[1]

read_len = 151 + 2 + 151 # + ~58 header

from collections import defaultdict
barcodes = defaultdict(int)

with gzip.open(fqname, 'rb') as fq:
    for i, line in enumerate(fq):
        if i % 4 == 0: # This is a header
            barcode = line[-9:-1]
            #barcode = line.rsplit(b":", 1)[1].rstrip()
            barcodes[barcode] += 1

#print(barcodes)
