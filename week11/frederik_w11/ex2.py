#!/usr/bin/env python3

import sys
#from collections import defaultdict

if len(sys.argv) == 2:
    fasta_file = sys.argv[1]
else:
    print("Must specifiy exactly one argument: fasta file.")
    sys.exit(1)

def fasta_entries(fp):
    name, seq = None, []
    for line in fp:
        line = line.rstrip()
        if line.startswith('>'):
            if name:  
                yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)
    if name: yield (name, ''.join(seq))

def translate_num_to_str(num, k):
    num_str_arr = []
    mask = 0b11
    while num > 0:
        n = num & mask
        if n == 0b00:
            num_str_arr.append('a')
        elif n == 0b11:
            num_str_arr.append('t')
        elif n == 0b01:
            num_str_arr.append('c')
        elif n == 0b10:
            num_str_arr.append('g')
        num >>= 2
    num_str = "".join(num_str_arr[::-1])
    if len(num_str) < k:
        num_str = (k - len(num_str)) * 'a' + num_str
    return num_str

KMER_LENGTH = 10
# Bitarrays would be nice, but do not exist natively in python
kmer_dict = bytearray(2**(2*KMER_LENGTH))

def kmers(seq, k):
    if len(seq) < k:
        print(len(seq), k)
        return
    
    mask = int(k * '11', 2)

    num = 0
    counter = k
    counter_max = len(seq)

    new_kmer = True

    # Consider that the time saved from the while loop counter skips
    # probably is lost (and more), if it doesn't happen often. Then the
    # C-like for loop is better.
    while counter < counter_max:
        if new_kmer:
            num = 0
            new_kmer = False
            for i, char in enumerate(seq[counter - k : counter]):
                num <<= 2
                if char == 'a':
                    pass
                elif char == 't':
                    num |= 0b11
                elif char == 'c':
                    num |= 0b01
                elif char == 'g':
                    num |= 0b10
                else:
                    new_kmer = True
                    counter += i + 1
                    break
            if new_kmer:
                continue
        else:
            char = seq[counter]
            num <<= 2
            if char == 'a':
                pass
            elif char == 't':
                num |= 0b11
            elif char == 'c':
                num |= 0b01
            elif char == 'g':
                num |= 0b10
            else:
                new_kmer = True
                counter += k
                continue
            num &= mask

        counter += 1
        if kmer_dict[num] < 2:
            kmer_dict[num] += 1

with open(fasta_file, "r") as f:
    for header, seq in fasta_entries(f):
        kmers(seq, KMER_LENGTH)



max_c = 10
for key, value in enumerate(kmer_dict):
    if value == 1 and max_c != 0:
        print(f"{translate_num_to_str(key, KMER_LENGTH)} ({key}): {value}")
        max_c -= 1
print(f"Total: {sum(kmer_dict)}")
#kmer_dict
