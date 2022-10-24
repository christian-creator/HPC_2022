#!/usr/bin/env python3

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__, reverse=True)

# Read file in
items = []
sizes = []
values = []
density = []

with open("../../../knapsack.lst", "r") as f:
    header = f.readline()
    for line in f:
        item, size, value = line.strip().split("\t")
        items.append(item)
        sizes.append(float(size))
        values.append(float(value))
        density.append(float(value) / float(size))
        #if len(items) == 20:
        #    break

argsort_density = argsort(density)

sizes = [sizes[i] for i in argsort_density]
items = [items[i] for i in argsort_density]
values = [values[i] for i in argsort_density]
density = [density[i] for i in argsort_density]

maxsize = 342
problem = 'X' * len(items)
bestproblem = ''
bestvalue = 0
stack = [problem]

while len(stack) > 0:
    problem = stack.pop()
    # Calculate bound/estimate and constraint of choices
    
    size = sum((sizes[i] for i, x in enumerate(problem) if x=="1"))
    estimate_size = size
    estimate = sum((values[i] for i, x in enumerate(problem) if x=="1"))
    for i in range(problem.find('X'), len(items)):
        if estimate_size + sizes[i] > maxsize:
            estimate += (maxsize - estimate_size) * density[i]
            break
        else: 
            estimate_size += sizes[i]
            estimate += values[i]

    # if bound/estimate is worse than any previous found solution, discard
    if estimate < bestvalue:
        continue
    
    # Are constraints exceeded, discard
    if size > maxsize:
        continue
    
    # Still not solved, then split the problem
    if 'X' in problem:
        nextx = problem.find('X')
        # Important optimization: put the 1 at the end - this way the tree searches the 
        # for solutions where the largest item is in the solution. 
        stack.append(problem[:nextx] + '0' + problem[nextx+1:])
        stack.append(problem[:nextx] + '1' + problem[nextx+1:])
    
    # Solved, is the better than any solution so far?
    elif estimate > bestvalue:
        bestvalue = estimate
        bestproblem = problem
    # DEBUG: What is going on with the stack???
    # print(stack)

# Output
print(f"Best problem (estimate: {bestvalue}):", bestproblem)
print("Items:", *[item for item, sol in zip(items, bestproblem) if sol == "1"])
print("Combined weight:", sum((sizes[i] for i, x in enumerate(bestproblem) if x=="1")))
print("Combined value:", sum((values[i] for i, x in enumerate(bestproblem) if x=="1")))

