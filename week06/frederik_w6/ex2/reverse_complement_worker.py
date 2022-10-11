#!/usr/bin/env python3

import sys

if len(sys.argv) != 2:
    print("Needs exactly one argument")
    sys.exit(1)

input_fasta = sys.argv[1]
output_fasta = ".reverse_complement.".join(input_fasta.rsplit("."))

seq = []

# Binary read and write
with open(input_fasta, "rb") as fp, open(output_fasta, "wb") as fo:
    for line in fp:
        if line.startswith(b'>'):
            name = line
        else:
            seq.append(line[:-1])

    seq_str = b''.join(seq)
    complement = seq_str.maketrans(b"atcg", b"tagc")

    # Translating the entire string to complement with the native method.
    seq_str = seq_str.translate(complement)[:-1]
        
    # Using count is faster than using a dictionary for the values, as it
    # utilises a C loop within the implementation.
    a_count = seq_str.count(b'a')
    c_count = seq_str.count(b'c')
    g_count = seq_str.count(b'g')
    t_count = seq_str.count(b't')
    n_count = seq_str.count(b'n')
        
    fo.write(name[:-1] + b" a:" + str(a_count).encode('ascii') + 
                        b" c:" + str(c_count).encode('ascii') +
                        b" g:" + str(g_count).encode('ascii') +
                        b" t:" + str(t_count).encode('ascii') +
                        b" n:" + str(n_count).encode('ascii') + b'\n')  
        
    for i in range(0,len(seq_str), 60): 
        fo.write(seq_str[i: i+60])
        fo.write(b"\n")

