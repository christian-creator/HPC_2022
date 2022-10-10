#!/usr/bin/env python3

# Libraries
import subprocess
import os
import time

# Qsub function
def submit2(command, runtime, cores, ram, directory='', modules='', group='pr_course',
    output='/dev/null', error='/dev/null'):
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
    group:     Accounting - which group pays for the compute.
    output:    Output file of your job.
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


# Reading files
infile_path = "/home/projects/pr_course/human.fsa"

# Initialising variables
file_count = 1
filename_collector = list()

# Splitting the files
with open(infile_path, "rb") as in_fi:
    first = False
    for line in in_fi:
        if line.startswith(b">"):
            if first:
                tf.close()
                submit2(f'python work.py -f {file_count}.fasta_sequence_temp.fsa',runtime=10, cores=1, ram=2,  directory='', modules='tools anaconda3/4.4.0')
                file_count += 1
                tf = open("{}.fasta_sequence_temp.fsa".format(file_count), "wb")
                tf.write(line)
            else:
                tf = open("{}.fasta_sequence_temp.fsa".format(file_count), "wb")
                tf.write(line)
                first = True
        else:
            tf.write(line)

tf.close()

submit2(f'python work.py -f {file_count}.fasta_sequence_temp.fsa', runtime=10, cores=1, ram=2, directory='', modules='tools anaconda3/4.4.0')

#Waiting for all files to be complete
for i in range(1,file_count):
    if os.path.exists("output_{}.fasta_sequence_temp.fsa".format(i)):
        continue
    else:
        time.sleep(10)

outfile_complete = open("human_comp_rev.fsa", "wb")

with open("human_comp_rev.fsa", "wb") as fo:
    for i in range(1, file_count + 1):
        infile_name = "output_{}.fasta_sequence_temp.fsa".format(i)
        infile_temp = open(infile_name, "rb")

        # Copying lines into output file
        for line in infile_temp:
            fo.write(line)

       	infile_temp.close()
        
	# Deleting temporary files
        subprocess.call(['rm', '{}.fasta_sequence_temp.fsa'.format(i)])
        subprocess.call(['rm','output_{}.fasta_sequence_temp.fsa'.format(i)])



