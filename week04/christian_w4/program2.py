infile = open('../../human.fsa', 'rb')
outfile = open('human.fsa', 'wb')
for line in infile:
    outfile.write(line)
infile.close()
outfile.close()

