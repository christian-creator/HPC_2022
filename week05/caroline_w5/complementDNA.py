#!/usr/bin/env python3

"""
TIME:
real	0m57.963s
user	0m43.804s
sys	0m9.395s

Thoughts on optimization:
In order to optimize the code, I used the build-in function count, which is 
faster compared to using if-statements. Then I tried to implement reading 
and writing but I could not get this to work. I only got bytes to work for
reading, but then the code took way longer to execute.So, even though I did 
not do a lot of optimizing the code still ran quite well, which I am a bit 
surprised about. 
"""

# Reading files
infile_path = "/home/projects/pr_course/human.fsa"
outfile_path = "/home/projects/pr_course/people/carmar/week05/comphuman.fsa"

infile = open(infile_path, "r")
outfile = open(outfile_path, "w")

# Initialise helper functions and variables
translationTable = str.maketrans("atcg","tagc")
com_DNA = ""
header = ""

# Function for counting bases in the entry_line
def bases_count (entry_line):
    A_count = entry_line.count("a")
    T_count = entry_line.count("t")
    C_count = entry_line.count("c")
    G_count = entry_line.count("g")
    N_count = entry_line.count("n")

    #print("A:", A_count, "T:", T_count, "C:", C_count, "G:", G_count, "Other:", N_count)

    return A_count, T_count, C_count, G_count, N_count

# Main script
for line in infile:
    if line.startswith(">"):
        if com_DNA != "":
            # Counting bases
            A_count, T_count, C_count, G_count, N_count = bases_count(com_DNA)
            # Printing information about entry
            outfile.write(header)
            outfile.write(" (A: %i, T: %i, C: %i G: %i Other: %i) \n" % (A_count, T_count, C_count, G_count, N_count))
            # Printing and complementing strand
            com_DNA = com_DNA.translate(translationTable)
            outfile.write(com_DNA)
            # Getting ready for next entry
            header = line.replace("\n", "")
            com_DNA = ""
            continue
        else:
            # This is for the first entry
            header = line.replace("\n", "")
            continue
    else:
        com_DNA += line

# Printing for the last entry
outfile.write(header)
outfile.write(" (A: %i, T: %i, C: %i G: %i Other: %i) \n" % (A_count, T_count, C_count, G_count, N_count))
com_DNA = com_DNA.translate(translationTable)
outfile.write(com_DNA)

# Closing files
infile.close()
outfile.close()
