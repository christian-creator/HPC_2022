#!/usr/bin/env python3

# Runtime:
# real	1m14.400s
# user	0m42.422s
# sys	0m8.187s

import sys

if len(sys.argv) != 2:
    print("Needs exactly one argument")
    sys.exit(1)

input_fasta = sys.argv[1]
output_fasta = "complement.fasta"

def read_from_fasta(fp):
    name, seq = None, []
    for line in fp:
        # Stripping the lines is not needed as the lines should be outputted 
        # with newlines anyway.
        # line = line.rstrip()
        if line.startswith(b'>'):
            if name: yield (name, seq)
            name, seq = line, []
        else:
            seq.append(line)
    if name: yield (name, seq)

# Binary read and write
with open(input_fasta, "rb") as fp, open(output_fasta, "wb") as fo:
    for name, seq in read_from_fasta(fp):
        seq_str = b''.join(seq)

        # Translating the entire string to complement with the native method.
        complement = seq_str.maketrans(b"atcg", b"tagc")
        seq_str = seq_str.translate(complement)
        
        # Using count is faster than using a dictionary for the values, as it
        # utilises a C loop within the implementation.
        a_count = seq_str.count(b'a')
        c_count = seq_str.count(b'c')
        g_count = seq_str.count(b'g')
        t_count = seq_str.count(b't')
        n_count = seq_str.count(b'n')
        
        fo.write(name[:-1] + b"a:" + str(a_count).encode('ascii') + 
                        b"c:" + str(c_count).encode('ascii') +
                        b"g:" + str(g_count).encode('ascii') +
                        b"t:" + str(t_count).encode('ascii') +
                        b"n:" + str(n_count).encode('ascii') + b'\n')  
        
        fo.write(seq_str)
