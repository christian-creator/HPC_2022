import hashlib
import sys
import time
from datetime import datetime
from joblib import Parallel, delayed

if len(sys.argv) != 2:
    print("Only needs file-path")
    sys.exit(1)

input_fasta = sys.argv[1]

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

def setbit(bloomfilter, byteposition, bitposition):
    bloomfilter[byteposition] |= 1 << bitposition

def isbitset(bloomfilter, byteposition, bitposition):
    return (bloomfilter[byteposition] & (1 << bitposition)) != 0

def add_kmers_to_bloomfilter(seq,k,n,sample=None):
    """Add K-mers to global bloo_filter byte-array

    Args:
        seq (binary-string): input-fasta
        k (int): Number of hash functions
        n (int): Len of byte-array
        sample (int, optional): Percentage of the entire seq to index. Used for testing. Defaults to None.
    """
    global bloom_filter,kmers
    if sample:
        seq = seq[:int(len(seq)/sample)]
    for kmer in generate_kmers(seq,30):
        # result = hashlib.md5(kmer)
        result = hashlib.sha256(kmer)
        result = result.digest()
        for i in range(k):
            index = int.from_bytes(result[i:-(k-i)], byteorder=sys.byteorder) % (n)
            setbit(bloom_filter,index,i)

start_time = datetime.now()

# sample_size = 1
n = int(34359738368/8)
k = int(4) # Human CHR1 + Human test
bloom_filter = bytearray(n)

with open(input_fasta,"rb") as infile:
    # result = Parallel(n_jobs=7,verbose=69,backend="threading")(delayed(add_kmers_to_bloomfilter)(seq,k,n) for name,seq in read_fasta(infile))
    for i,(name, seq) in enumerate(read_fasta(infile)):
        print(f"Entry N:{i} is being indexed into bloom")
        add_kmers_to_bloomfilter(seq,k,n) # ,sample=sample_size

end_time = datetime.now()
with open("bloom_filter.dat", "wb") as binary_file:
    binary_file.write(bloom_filter)

print("Time to run entire programme: ",datetime.now()-start_time)

"""
Time to run entire programme:  5:10:15.030675
"""
