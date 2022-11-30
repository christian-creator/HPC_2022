#!/usr/bin/env python3

import sys
import gzip
from collections import defaultdict
from contextlib import ExitStack

if len(sys.argv) != 2:
    print("Supply just one argument, file.")
    sys.exit(1)

fqname = sys.argv[1]

skip_len = 151 + 2 + 151 # + ~58 header

barcodes = defaultdict(int)
barcode_at_idx = list()

with gzip.open(fqname, 'rb') as fq:
    while True:
        line = fq.readline()
        if line == b'':
            break
        _ = fq.read(skip_len)
        barcode = line[-9:-1]
        barcodes[barcode] += 1
        barcode_at_idx.append(barcode)

ERROR = 1

barcodes_error_corrected = dict()

prev_count = None
all_true_barcodes_found = False

for barcode, count in sorted(barcodes.items(), key=lambda item: -item[1]):
    found = False
    
    if prev_count is None:
        prev_count = count
    elif prev_count // 5 > count:
        break

    for barcode_ec in barcodes_error_corrected.keys():
        if sum(a != b for a, b in zip(barcode, barcode_ec)) <= ERROR:
            barcodes_error_corrected[barcode_ec] += count
            found = True
            break

    if not found and not all_true_barcodes_found:
        prev_count = count
        barcodes_error_corrected[barcode] = count

print(barcodes_error_corrected)
print(len(barcodes_error_corrected.keys()))

flist = [f'ngs_{key}.fastq' for key in barcodes_error_corrected.keys()]

from joblib import Parallel, delayed

def 
with gzip.open(fqname, 'rb') as fq:
    with ExitStack() as stack:
        files = {key: stack.enter_context(gzip.open(f"ngs_{key.decode('utf-8')}.fq.gz", "wb")) for key in barcodes_error_corrected.keys()}
        for barcode in barcode_at_idx:
            line = fq.readline()
            if line == b'':
                break
            rest = fq.read(skip_len)
            if barcode in files:
                files[barcode].write(line+rest)
            
result = Parallel(n_jobs=N_JOBS, verbose=69)(delayed(entry_bloomfilter)(index, file_name_prefix) for i, index in enumerate(index_fasta(input_fasta)))
