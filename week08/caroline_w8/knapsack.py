#!/usr/bin/env python3

"""
Time for 100 items: 7.13s
"""

# Libraries
import pandas as pd
import numpy as np

# Lists for items and their values
items = list()
size = list()
values = list()
valuePsize = list()

# Reading file and putting each column into separate list
infile = open("knapsack.lst", "r")
header = infile.readline()
for line in infile:
    item, item_size, item_value = line.split()
    items.append(item)
    size.append(float(item_size))
    values.append(float(item_value))
    valuePsize.append(float(item_value)/float(item_size))

infile.close()

# Finding index to sort after.
valuePsize_sort_index = np.argsort(valuePsize)[::-1]

items = np.array(items)[valuePsize_sort_index]
size = np.array(size)[valuePsize_sort_index]
values = np.array(values)[valuePsize_sort_index]

# Initializing values for algorithm
maxsize = 342
problem = 'X' * len(items)
bestproblem = ''
bestvalue = 0
bestsize = 0
stack = [problem]


while len(stack) > 0:
    problem = stack.pop()
    # Calculate bound/estimate and constraint of choices
    estimate_size = 0
    estimate = 0

    for i in range(len(problem)):
        if problem[i] == "1":
            estimate_size += size[i]
            estimate +=  values[i]
        # This loop checks how many of the following items can fit.
        if problem[i] == "X":
            if estimate_size + size[i] < maxsize:
                estimate += values[i]
                estimate_size += size[i]
            # Here only a fraction of an item is added, if the whole thing does not fit
            else:
                if abs(maxsize - estimate_size) != 0:
                    estimate += abs(maxsize - estimate_size) * values[i]/size[i]
                    break

    # if bound/estimate is worse than any previous found solution, discard
    if estimate < bestvalue:
        continue
    # Are constraints exceeded, discard
    if estimate_size > maxsize:
        continue
    # Still not solved, then split the problem
    if 'X' in problem:
        nextx = problem.find('X')
        stack.append(problem[:nextx] + '1' + problem[nextx+1:])
        stack.append(problem[:nextx] + '0' + problem[nextx+1:])
    # Solved, is the better than any solution so far?
    elif estimate > bestvalue:
        bestvalue = estimate
        bestproblem = problem
        bestsize = estimate_size

# Printing results
print("The best problem:", bestproblem)
print("Combined size:", bestsize)
print("Combined value:", bestvalue)
