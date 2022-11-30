import sys
import math

# 1) Computing the Bloom filter parameters
# To find the number of possibilities we claculate the number max number of unique 30-mers in the chromosome. This, can be calculated with the followign equation:
# Lenght of chromosome - K-mer size. If the score is below 4^30 we will use that score as the maximum number of 30-mers.


def read_fasta(fp):
    name, seq = None, []
    for line in fp:
        line = line.rstrip()
        if line.startswith(">"):
            if name: yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)
    if name: yield (name, ''.join(seq))

if len(sys.argv) != 2:
    print("Only needs file-path")
    sys.exit(1)

input_fasta = sys.argv[1]

chromsome_len = 0
with open(input_fasta,"r") as infile:
    for name, seq in read_fasta(infile):
        chromsome_len += len(seq)


kmer_length = 30
error_rate = 0.01
n = chromsome_len-30
m = (-n*math.log(error_rate)) / (math.log(2)**2)
m_next_power = math.floor(math.log(m)/math.log(2)) + 1 # Solve 2^x = y for x
m_corrected = 2**m_next_power

k = -math.log(error_rate)/math.log(2)
p = (1-math.exp(-k*n/m_corrected))**k

print(f"Desired error-rate {error_rate:.2f}",
    f"Number of elements n: {n:.0f}",
    f"The size of the bit array m ~ to the next power of 2: {m_corrected:.0f}",
    f"The number of the hash functions k: {k:.2f}",
    f"The Error rate: {p:.5f}",
    sep="\n")

print("Memory specifications:",
    f"Bytes m_corrected/8: {m_corrected/8:.2f}",
    f"Gigabyts used in memory: {(m_corrected/8)/1_073_741_824}",
    sep="\n")


# I'm going to use the md5 function which returns 16 byte encoding of a binary string. I use this functions since it is
# since the function itself is collision resistant, uniform and non-continuos. Furthermore as it returns 16 bytes: 16^32 it
# has much more possible maping 2^128 possibilities comapred to the used number which is 4294967296: 2^128-4294967296~ 3^32 un mapped options.
# To create different hash function i will use different slices of the 128 bits. Corresponding to the flor(128-k) = 121. This corresponds to
# 2^121 different combinations
# Number of elements n: 3088269802
# The size of the bit array m ~ to the next power of 2: 34359738368
# The number of the hash functions k: 6.64
# The Error rate: 0.00494
# Memory specifications:
# Bytes m_corrected/8: 4294967296.00
# Gigabyts used in memory: 4.0
