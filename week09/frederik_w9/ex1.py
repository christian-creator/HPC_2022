#!/usr/bin/env python3

import sys
import subprocess
from joblib import Parallel, delayed

if len(sys.argv) != 2:
    print("Needs exactly one argument")
    sys.exit(1)

input_fasta = sys.argv[1]
output_fasta = "complement.fasta"

def fasta_entries(fp):
    name, seq = None, []
    for line in fp:
        line = line.rstrip()
        if line.startswith(b'>'):
            if name:  
                yield (name, seq)
            name, seq = line, []
        else:
            seq.append(line)
    if name: yield (name, seq)

def reverse_complement(header, seq): 
    seq_str = b''.join(seq)
    complement = seq_str.maketrans(b"atcg", b"tagc")

    seq_str = seq_str.translate(complement)[::-1]
        
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

with open(input_fasta, "rb") as f:
    result = Parallel(n_jobs=8)(delayed(reverse_complement)(header, seq) for header, seq in fasta_entries(f))

with open(output_fasta, "wb") as f:
    for header, seq in result:
        f.write(header)
        f.write(seq)
        f.write(b'\n')



