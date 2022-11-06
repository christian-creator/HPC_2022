#!/usr/bin/env python3

import sys
import subprocess
from joblib import Parallel, delayed

if len(sys.argv) != 2:
    print("Usage: ex2.py <input fasta file>");
    sys.exit(1)

input_fasta = sys.argv[1]
#output_fasta_index = "fasta.idx"
output_fasta = "complement.fasta"

def index_fasta(input_fasta):
    try:
        infile = open(input_fasta, 'rb')
    except IOError as err:
        print("Cant open file:", str(err));
        sys.exit(1)

    chunksize = 1024*1024 # 1 MB
    filepos = 0
    headers = list()
    newlines = list()

    while True:
        content = infile.read(chunksize)
        if len(content) == 0:
            break
        # find headers
        chunkpos = 0
        while chunkpos != -1:
            chunkpos = content.find(b'>', chunkpos)
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


def reverse_complement(index):
    header_start, header_end, seq_start, seq_end = index

    with open(input_fasta, "rb") as f:
        # get header and sequence
        f.seek(int(header_start))
        header = f.read(int(header_end) - int(header_start)+1)
        f.seek(int(seq_start))
        seq_str = f.read(int(seq_end) - int(seq_start)+1)
        
    #seq_str = b''.join(seq)
    complement = seq_str.maketrans(b"atcg", b"tagc")

    seq_str = seq_str.replace(b"\n", b"").translate(complement)[::-1]
        
    a = seq_str.count(b'a')
    c = seq_str.count(b'c')
    g = seq_str.count(b'g')
    t = seq_str.count(b't')
    n = seq_str.count(b'n')
   
    header = (header[:-1] + b" a:" + str(a).encode('ascii') + 
                        b" c:" + str(c).encode('ascii') +
                        b" g:" + str(g).encode('ascii') +
                        b" t:" + str(t).encode('ascii') +
                        b" n:" + str(n).encode('ascii') + b'\n')  
    
    reverse_complement_out = b"\n".join(seq_str[i: i+60] for i in range(0, len(seq_str), 60))
    return header, reverse_complement_out

result = Parallel(n_jobs=8)(delayed(reverse_complement)(index) for index in index_fasta(input_fasta))

with open(input_fasta, "wb") as f:
    for header, seq in result:
        f.write(header)
        f.write(seq)
        f.write(b'\n')



