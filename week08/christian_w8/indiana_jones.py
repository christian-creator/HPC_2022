import sys
import os
import time
import copy

def read_list(path,max_index):
    item_names = []
    item_sizes = []
    item_values = []
    with open(path) as infile:
        for line in infile:
            if line[0] != "#":
                name, size, value = line.split()
                item_names.append(name)
                item_sizes.append(float(size))
                item_values.append(float(value))
    return item_names[:max_index], item_sizes[:max_index], item_values[:max_index]


def return_sum_of_items(problem,list_of_interest,verbose=None):
    if verbose:print(sum([list_of_interest[i] for i,x in enumerate(problem) if x == "1"]),"problem-in-function",problem,"list-of-interest",list_of_interest)
    
    return sum([list_of_interest[i] for i,x in enumerate(problem) if x == "1"])


def estimate_upperbound(problem,item_values,item_sizes,value_size_ratios):
    # Calculate intial size and estimate from values in list
    estimate = return_sum_of_items(problem,item_values)
    size = return_sum_of_items(problem,item_sizes)

    # Using a size-tracker to track the weights of the upper-bound
    size_tracker = size
    index_tracker = problem.find("X")

    if index_tracker == -1:
        return estimate, size

    while size_tracker <= maxsize and index_tracker != len(problem):
        estimate += item_values[index_tracker]
        size_tracker += item_sizes[index_tracker]
        index_tracker += 1
    
    # if the index tracker if not longer than the list of values
    if index_tracker < len(problem) - 1:
        remaining_size = size_tracker-maxsize
        estimate += value_size_ratios[index_tracker + 1] * remaining_size

    return estimate, size


path = "/Users/christianpederjacobsen/Dropbox/DTU/Civil/Master/3_semester/High performance computing/knapsack.lst"
item_names, item_sizes, item_values = read_list(path,-1)


# Sorting the lists by the value/size ratios.
value_size_ratio = [x/y for x,y in zip(item_values,item_sizes)]
item_names = [name for name, size_value_ratio in sorted(zip(item_names, value_size_ratio), key=lambda pair: pair[1],reverse=True)]
item_sizes = [size for size, size_value_ratio in sorted(zip(item_sizes, value_size_ratio), key=lambda pair: pair[1],reverse=True)]
item_values = [value for value, size_value_ratio in sorted(zip(item_values, value_size_ratio), key=lambda pair: pair[1],reverse=True)]
value_size_ratios = sorted(value_size_ratio,reverse=True)


maxsize = 342
problem = "X" * len(item_names)
bestproblem = ''
bestvalue = 0
stack = [problem]
start_time = time.time()


while len(stack) > 0:
    problem = stack.pop()
    # Calcualting the upper-bound estimate and the size of the problem
    estimate, size = estimate_upperbound(problem,item_values,item_sizes,value_size_ratios)

    # if bound/estimate is worse than any previous found solution, discard
    if estimate < bestvalue:
        continue
    # Are constraints exceeded, discard
    if size > maxsize:
        continue
   
   # Still not solved, then split the problem
    if 'X' in problem:
        nextx = problem.find('X')
        stack.append(problem[:nextx] + '0' + problem[nextx+1:])
        # I found that changing the order of the append was a signficant optimizaiton.
        # Most likely this is due us firstly searching the tree where the items with the highest value/weight is included.
        # Since they have the value/weight score most likely they will be a part of the best solution. 
        stack.append(problem[:nextx] + '1' + problem[nextx+1:])
        
        
    # Solved, is the better than any solution so far?
    elif estimate > bestvalue:
        bestvalue = estimate
        bestproblem = problem



print(bestvalue,bestproblem,str(bestproblem.count("1")),return_sum_of_items(bestproblem,item_sizes),sep="\n")
"""
### bestvalue: 3000.8000000000006
### bestproblem: 111111111111111111101000000000000000000000000000000000000000000000000000000000000000000000000000000
### 1-count: 20
### Weight of best problem 341.79999999999995
"""
print("--- %s seconds ---" % (time.time() - start_time))
"""
### Time 3.14 seconds
"""

# I was unable to find the best solution going to a 1/10 of a second. I am unsure, which optimization steps i need. or whether it is because i use a while-loop rather
# Than a for-loop... However i doubt that this is the case.