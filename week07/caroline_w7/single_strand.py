#!/usr/bin/env python3

# Libraries
import sys

# Get the right input
file_path = sys.argv[1]
header_start = sys.argv[2]
header_end = sys.argv[3]
seq_start = sys.argv[4]
seq_end = sys.argv[5]

# Finding it in the file
u_file = open(file_path, "rb")

# Printing header
u_file.seek(int(header_start))
header = u_file.read(int(seq_end) - int(header_start))
print(header.decode("utf-8"))

# Closing file
u_file.close()
