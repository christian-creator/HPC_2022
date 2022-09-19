infile = open('../../human.fsa', 'r')
outfile = open('human.fsa', 'w')
line = infile.readline()
while line != '':
    outfile.write(line)
    line = infile.readline()

