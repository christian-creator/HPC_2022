infile = open('../../human.fsa', 'r')
outfile = open('human.fsa', 'w')
for line in infile:
    outfile.write(line)
infile.close()
outfile.close()

