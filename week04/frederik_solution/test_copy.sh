#!/bin/bash

echo "Copy using while loop"
time ./copy1.py

echo "Copy using for loop"
time ./copy2.py

echo "Copy using for loop w/ binary rw"
time ./copy3.py

echo "Copy using chunks of 10k"
time ./copy4.py

echo "Copy using cp"
time cp /home/projects/pr_course/human.fsa /home/projects/pr_course/people/fregad/human.fsa
