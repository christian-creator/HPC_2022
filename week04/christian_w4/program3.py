infile = open('../../human.fsa', 'rb')
outfile = open('human.fsa', 'wb')
while True:
    chunck = infile.read(10000)
    outfile.write(chunck)
    if len(chunck) < 10000:
        break
infile.close()
outfile.close()

