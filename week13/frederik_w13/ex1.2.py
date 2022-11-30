#!/usr/bin/env python3

import sys
import gzip

if len(sys.argv) != 2:
    print("Supply just one argument, file.")
    sys.exit(1)

fqname = sys.argv[1]

skip_len = 151 + 2 + 151 # + ~58 header

from collections import defaultdict
barcodes = defaultdict(int)

def read_fq(input_fq):
    try:
        infile = open(input_fq, 'rb')
    except IOError as err:
        print("Cant open file:", str(err));
        sys.exit(1)

    chunksize = 1024*1024 # 1 MB
    filepos = 0
    barcodes = []
    headers = list()
    newlines = list()

    while True:
        content = infile.read(chunksize)
        if len(content) == 0:
            break
        # find headers
        chunkpos = 0
        while chunkpos != -1:
            chunkpos = content.find(b'@S', chunkpos)
            if chunkpos != -1:
                headers.append(chunkpos + filepos)
                chunkpos += 1
        # find corresponding newlines
        for i in range(len(newlines), len(headers)):
            chunkpos = max(0, headers[i] - filepos)
            chunkpos = content.find(b'\n', chunkpos)
            if chunkpos != -1:
                newlines.append(chunkpos + filepos)
        filepos += len(content)
    infile.close()

    # printing 
    for i in range(len(headers)):
        headstart = headers[i]
        headend = newlines[i]
        seqstart = headend + 1
        if i < len(headers) - 1:
            seqend = headers[i+1] - 1
        else:
            seqend = filepos - 1
        print(headstart, headend, seqstart, seqend)
        yield (headstart, headend, seqstart, seqend)


read_fq(fqname)

"""
    while True:
        line = fq.readline()
        if line == b'':
            break
        _ = fq.read(skip_len)
        barcode = line.rsplit(b":", 1)[1].rstrip()
        barcodes[barcode] += 1
"""
