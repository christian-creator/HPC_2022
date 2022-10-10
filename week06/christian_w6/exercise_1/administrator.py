import sys
import os
import argparse
from datetime import datetime
import subprocess


def get_parser():
    # Build commandline parser
    parser = argparse.ArgumentParser(
        description="Description of what the script does")
    # Arguments
    parser.add_argument("-in", "--infile", type=str, dest="infile",
                        metavar="FILE",
                        help="The inputfile to calculate complement strads")
    
    parser.add_argument("-tmp", "--tmp_dir", type=str, dest="tmp_dir",
                        metavar="PATH",
                        help="The tmp directory for single fasta files")
    
    parser.add_argument("-out", "--out_dir", type=str, dest="out_dir",
                        metavar="PATH",
                        help="The outputdirectory for tmp files")
    return parser


def get_args():
    parser = get_parser()
    args = parser.parse_args()
    return args


def submit2(command, runtime, cores, ram, directory='', modules='', group='pr_course', output='/dev/null', error='/dev/null'):
    """
    Function to submit a job to the Queueing System - without jobscript file
    Parameters are:
    command:   The command/program you want executed together with any parameters.
               Must use full path unless the directory is given and program is there. 
    directory: Working directory - where should your program run, place of your data.
               If not specified, uses current directory.
    modules:   String of space separated modules needed for the run.
    runtime:   Time in minutes set aside for execution of the job.
    cores:     How many cores are used for the job.
    ram:       How much memory in GB is used for the job.
    output:    Output file of your job.
    group:     Accounting - which group pays for the compute.
    error:     Error file of your job.
    """
    runtime = int(runtime)
    cores = int(cores)
    ram = int(ram)
    if cores > 10:
        print("Can't use more than 10 cores on a node")
        sys.exit(1)
    if ram > 120:
        print("Can't use more than 120 GB on a node")
        sys.exit(1)
    if runtime < 1:
        print("Must allocate at least 1 minute runtime")
        sys.exit(1)
    minutes = runtime % 60
    hours = int(runtime/60)
    walltime = "{:d}:{:02d}:00".format(hours, minutes)
    if directory == '':
        directory = os.getcwd()
    # Making a jobscript
    script = '#!/bin/sh\n'
    script += '#PBS -A ' + group + ' -W group_list=' + group + '\n'
    script += '#PBS -e ' + error + ' -o ' + output + '\n'
    script += '#PBS -d ' + directory + '\n'
    script += '#PBS -l nodes=1:ppn=' + str(cores) + ',mem=' + str(ram) + 'GB' + '\n'
    script += '#PBS -l walltime=' + walltime + '\n'
    if modules != '':
        script += 'module load ' + modules + '\n'
    script += command + '\n'
    # The submit
    job = subprocess.run(['qsub'], input=script, stdout=subprocess.PIPE, universal_newlines=True) 
    jobid = job.stdout.split('.')[0]
    return jobid



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



def Administrator(infile):
    with open(infile) as fp:
        outfile_counter = 0 
        for name, seq in read_fasta(fp):
            # Name of TMP file
            input_fasta_name = f"tmp/fasta_entry_{outfile_counter}.fa"
            # Create TMP file
            input_fasta = open(input_fasta_name,"w+")
            # Write fasta entry to file
            input_fasta.write(name + "\n" + seq)
            input_fasta.close()
            # Call the worker on the infile script
            # Local
            output_file_name = f"translated/fasta_entry_{outfile_counter}_rev_comp.fa"
            print(f"Running {output_file_name}")
            # job = subprocess.run(["python3","worker.py","-i",input_fasta_name,"-o",output_file_name])
            # Qsub
            submit2(f"python3 worker.py -i {input_fasta_name} -o {output_file_name}", 1, 1, 5, directory='', modules='', group='pr_course', output='/dev/null', error='/dev/null')
            outfile_counter += 1
    

def main(args):
    # put your code here
    job = subprocess.run(['mkdir',"-p", args.tmp_dir])
    job = subprocess.run(['mkdir',"-p", args.out_dir])
    Administrator(args.infile)


if __name__ == "__main__":
    start_time = datetime.now()
    args = get_args()
    main(args)
    end_time = datetime.now()
