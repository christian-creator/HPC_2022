import sys
import argparse
from datetime import datetime
import time
from joblib import Parallel, delayed


def get_parser():
    # Build commandline parser
    parser = argparse.ArgumentParser(
        description="Description of what the script does")
    # Arguments
    parser.add_argument("-in", "--infile", type=str, dest="infile",
                        metavar="FILE",
                        help="The inputfile to calculate complement strads")
    return parser


def get_args():
    parser = get_parser()
    args = parser.parse_args()
    return args


# Functions for the indexing
def find_all(a_str, pattern):
    start = 0
    while True:
        start = a_str.find(pattern, start)
        if start == -1:
            return
        yield start
        start += len(pattern)  # use start += 1 to find overlapping matches

def Indexer(path_infile, index_file):
    """The optimized Indexer reads the fasta file in chunks and instead of iterating over the chunks it looks for the header start ">" 
       and then calculates every entry postion relative to the header starts.
    Args:
        path_infile (str): path to fasta-file it should index
        index_file (str): path to the output index file
    """
    index_file = open(index_file, "w+")
    # For timing the indexers
    start = time.time()
    # Miscellaneous variables for indexing
    first_header = True
    tracker = 0 # The tracker is used to track what chunk we are in with the number of bytes in each chunk
    with open(path_infile, "rb") as infile:
        while True:
            chunk = infile.read(100000)
            # Finds all ">" in the chunk and gives the byte position
            all_headers = list(find_all(chunk, b">"))
            # There can more than 1 header in a chunk therefore i iterate over a list
            if len(all_headers) > 0:
                for header_index in all_headers:
                    # The header position + what "chunk" we are in indicated by the tracker
                    header = header_index + tracker
                    # The end of the header is found by looking for the next newline.
                    end_header = chunk[header_index:].find(b"\n") + header
                    
                    # Here i just use a cheap trick for the right format.
                    if first_header is True:
                        index_file.write(
                            f"{header} {end_header} {end_header + 1} ")
                        first_header = False
                    else:
                        index_file.write(
                            f" {header - 1}\n{header} {end_header} {end_header + 1}")

            tracker += len(chunk)
            if len(chunk) < 100000:
                # When done i know that the last line is the sequence end of the last entry. 
                index_file.write(f" {tracker}\n")
                break

    index_file.close()
    end = time.time()
    print(f"Indexer Runtime of the indexing is: {end - start}")


def Reader(path_infile, coordinates):
    """ Returns the header and sequence from index coordinates"""
    
    h_start, h_end, seq_start, seq_end = [int(x) for x in coordinates.split()]

    with open(path_infile, "rb") as f:
        # get header and sequence
        f.seek(int(h_start))
        header = f.read(int(h_end) - int(h_start)+1)
        f.seek(int(seq_start))
        seq_str = f.read(int(seq_end) - int(seq_start)+1)
    
    seq_str = seq_str.replace(b"\n",b"")
    # seq_str = seq_str.decode("utf-8")
    return header, seq_str


def decode_bytestring_to_kmer(kmer_int,translation_table):
    """Used to return K-mer from integer"""
    bit_string = "{0:b}".format(kmer_int).rjust(20,"0")
    return "".join([translation_table[bit_string[i:i+2]] for i in range(0, 20, 2)])


def get_kmers(path_infile,index):
    """ Given an coordinates and the input-fastafile returns a bytearray with the k-mers indicating whether they 
       they are found 0, 1 or 2 times. 
       
       This is the main function which was "optimized". Multiple strategies was attempted
       including using while-loops (with a cool strategy to skip multiple k-mers with a wrong nucleotides), 
       translating the entire input string to our encodings of a,t,g,c using the regex library. However, no solution
       seem to be as fast as using two for-loops. The only cool thing is that i use binary string encodings meaning i 
       check for integer values. Furthermore, the K-mer is stopped for translation as soon as it sees a wrong nucelotide.
       This solution seemed to save 20% compared to not using binary strings and comparisons and seemed to be much faster
       than using Peters function. 

    Args:
        path_infile (str): Path to fasta-file
        index (str): Path to indexed fasta-file
        kmer_lengths (int): The kmer length
    Returns:
        bytearray: K-mer with counts being either 0,1,2
    """
    name, seq = Reader(path_infile,index)

    # Counting the k-mers by itertating over generator K-mers.
    counting_array = bytearray(4**10)
    seq = seq[:int(len(seq)/100)]
    kmer_lengt = 10
    
    for i in range(0,len(seq) - kmer_lengt):
        num = 0
        bad_entry = False
        # Itertaing over nuceotides in kmer
        for nuc in seq[i:i+kmer_lengt]:
            num <<= 2
            if nuc == 97: # a:0b1100001:97
                pass
            elif nuc == 116: # t:0b1110100:116
                num |= 0b11
            elif nuc == 103: # g:0b1100111:103
                num |= 0b01
            elif nuc == 99: # c:0b1100011:99
                num |= 0b10
            else:
                bad_entry = True
                break
        if not bad_entry:
            if 2 > counting_array[num]:
                counting_array[num] += 1 

    return counting_array



def Administrator(path_infile,index_file):
    # Load-balancing is acheived by sorting the indexes by the number of bytes thus acheiving Least-Load.
    coordinates = sorted([index.rstrip() for index in open(index_file,"r").readlines()], 
                            key=lambda x: int(x.split()[-1]) - int(x.split()[-2]),
                            reverse=True) 

    result = Parallel(n_jobs=7)(delayed(get_kmers)(path_infile, coord) for coord in coordinates)
    aggregated_counting_array = bytearray(4**10)

    # This solution is ONLY valid because there are a low number of chromsomes, since the sum 
    # can't be bigger than 248 and max-value in the counting array can thus be 2*Num_chromosomes.
    for i in range(len(aggregated_counting_array)):
        for array in result:
            aggregated_counting_array[i] += array[i]
    return aggregated_counting_array

def main(args): 
    index_file = "index.txt"
    Indexer(args.infile, index_file)
    aggregated_array = Administrator(args.infile,index_file)
    filtered_array = list(filter(lambda x: x == 1, aggregated_array))
    print("Size of the directory",sys.getsizeof(aggregated_array))
    print("How many different 10-mers are in the human genome?",len(aggregated_array))
    print("How many 10-mers in the human genome (file human.fsa) occur only once?",len(filtered_array))
    print("How many different 10-mers are possible? Length of chromosome - Kmer size:")


if __name__ == "__main__":
    start_time = datetime.now()
    args = get_args()
    main(args)
    end_time = datetime.now()
    print("Time to run entire programme: ",end_time-start_time)

"""
    Indexer Runtime of the indexing is: 1.3391869068145752
    Size of the directory 1048633 (3% of what we saw in previous exercise)
    How many different 10-mers are in the human genome? 1048576
    How many 10-mers in the human genome (file human.fsa) occur only once? 1
    How many different 10-mers are possible? (Length of chromosome - Kmer size):
    Time to run entire programme:  0:10:04.174992 (Saves 30%) 
 """