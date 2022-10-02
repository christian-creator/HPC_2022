#!/bin/sh
### Every line in this header section should start with ### for a comment
### or #PBS for an option for qsub
### Note: No unix commands may be executed until after the last #PBS line
###
### Account information
#PBS -W group_list=pr_course -A pr_course
##
### Send mail when job is aborted or terminates abnormally
#PBS -M s183493@dtu.dk
#PBS -m ae
###
### Compute resources, here 1 core on 1 node
#PBS -l nodes=1:ppn=1:thinnode
###
### Required RAM in GB
#PBS -l mem=10GB
###
### How long (max) will the job take
#PBS -l walltime=1:00:00
###
### Output files - not required to be specified
### Comment out the next 2 lines to use the job id instead in the file names
#PBS -e /home/projects/pr_course/people/carmar/week05/test.err
#PBS -o /home/projects/pr_course/people/carmar/week05/test.out
###
### More qsub options can be added here


# This part is the real job script
# Here follows the user commands:

# Load all required modules for the job
module load tools
module load anaconda3/4.4.0

# Running the code
cd /home/projects/pr_course/people/carmar/week05
time python comp2.py
