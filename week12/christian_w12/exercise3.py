import sys 
import os
import hashlib

if len(sys.argv) != 3:
    print("Needs Fasta-query, bloom-filter")
    sys.exit(1)

query_fasta = sys.argv[1]
path_bloom_filter = sys.argv[2]


# Reading the bloom filter
with open(path_bloom_filter, "rb") as binary_file:
    # Read the whole file at once
    bloom_filter = binary_file.read()

def isbitset(bloomfilter, byteposition, bitposition):
    return (bloomfilter[byteposition] & (1 << bitposition)) != 0

def read_fasta(fp):
    name, seq = None, []
    for line in fp:
        line = line.rstrip()
        if line.startswith(b">"):
            if name: yield (name, b''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)
    if name: yield (name, b''.join(seq))

def hashit(kmer):
    result = hashlib.md5(kmer)
    return int.from_bytes(result.digest(), byteorder=sys.byteorder)

def generate_kmers(input_string,kmer_length):
    """Generator used to create all possible K-mers from the sequence with the
       specified lengths. 
    Args:
        input_string (str): The chromosome sequence
        kmer_lengths (list): The kmer lengths
    Yields:
        str: Kmer
    """
    for i in range(len(input_string)-kmer_length):
        yield input_string[i:i+kmer_length]


def count_entries_kmers(seq,bloom_filter,k):
    counter = [0,0] # True, False
    for kmer in generate_kmers(seq,30):
        result = hashlib.sha256(kmer)
        result = result.digest()
        all_true_flag = True
        
        for i in range(k):
            index = int.from_bytes(result[i:-(k-i)], byteorder=sys.byteorder) % (n)
            if not isbitset(bloom_filter,index,i):
                all_true_flag = False
        if all_true_flag:
            counter[0] += 1
        else:
            counter[1] += 1
    return counter
            
k = int(4)
n = len(bloom_filter)

## MAIN
with open(query_fasta,"rb") as infile:
    for i,(name, seq) in enumerate(read_fasta(infile)):
        true_count,false_count = count_entries_kmers(seq,bloom_filter,k)
        print(name.decode("utf-8"), f"\nTrue count: {true_count}",f"False count: {false_count}")
        print()

"""
>NC_010448.4:c146896152-146802297 Sus scrofa isolate TJ Tabasco breed Duroc chromosome 6 
True count: 955 False count: 23375

>NC_006473.4:c32810205-32802845 Pan troglodytes isolate Yerkes chimp pedigree #C0471 (Clint) chromosome 6 
True count: 294 False count: 7037

>NC_000002.12:233760273-233773299 Homo sapiens chromosome 2, GRCh38.p7 Primary Assembly 
True count: 494 False count: 11904

>NC_015446.2:72027753-72032896 Solanum lycopersicum cultivar Heinz 1706 chromosome 9, SL2.50 
True count: 186 False count: 4928

>NW_018150443.1:296953-298260 Pichia kudriavzevii strain 129 chromosome Unknown BOH78_Sc010 
True count: 51 False count: 1227

>chromosome:GRCh38:MT:6846:8114:-1 Homo sapiens mitochondrion, 
True count: 38 False count: 1201
"""
