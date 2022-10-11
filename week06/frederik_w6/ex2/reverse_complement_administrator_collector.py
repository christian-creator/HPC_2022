#!/usr/bin/env python3

import sys
import time
import subprocess

if len(sys.argv) != 2:
    print("Needs exactly one argument")
    sys.exit(1)

input_fasta = sys.argv[1]
output_fasta = "complement.fasta"

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

file_no = 0

# Binary read and write
with open(input_fasta, "rb") as fp:
    name = False
    temp_f = open(f"temp_{file_no:03d}.fsa", "wb")
    for line in fp:
        if line.startswith(b'>'):
            if name: 
                temp_f.close()
                jobid = submit2(f"./reverse_complement_worker.py temp_{file_no:03d}.fsa", directory='/home/projects/pr_course/people/fregad/week06',
                    modules='tools anaconda3/4.0.0', runtime=10, cores=1, ram=2)
                file_no += 1
                temp_f = open(f"temp_{file_no:03d}.fsa", "wb")
            name = True
            temp_f.write(line)
        else:
            temp_f.write(line)
    temp_f.close()
    jobid = submit(f"./reverse_complement_worker.py temp_{file_no:03d}.fsa", directory='/home/projects/pr_course/people/fregad/week06',
        modules='tools anaconda3/4.0.0', runtime=10, cores=1, ram=2)

all_jobs = [f"temp_{i:03d}.fsa" for i in range(file_no)]
not_done_jobs = set(all_jobs)

while not_done_jobs:
    for job in list(not_done_jobs):
        if os.path.exists(job):
            not_done_jobs.remove(job)         
    time.sleep(5)

os.system("cat " + " ".join(all_jobs) + " > complement.fasta")

