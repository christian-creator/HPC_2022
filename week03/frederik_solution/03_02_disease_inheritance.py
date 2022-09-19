#!/usr/bin/env python

"""
Are there families who have had the same disease through 3 generations? Who and what disease in such case? It is not a trick question - you will find some.
In answering this question, then any type of cancer should just be regarded as cancer, i.e. the same disease (this is not true in reality). 3 generations should be understood as a ”straight line of inheritance”, i.e. child, father, father’s father/mother. Child, mother and father’s father is not straight.

If you look closely at your results, you will find some very interesting family patterns - such is the curse of (badly) generated data. 
"""

import mysql.connector
# Make database connection
cnx = mysql.connector.connect(user='s184260', passwd='OCiZxmrk', db='s184260')

# Create cursor
cur = cnx.cursor()

# Perform query
cur.execute('''SELECT cpr, biological_father, biological_mother FROM persons_week02''')

# Getting all rows
resultset = cur.fetchall()

family_tree = dict()

# Compute on resultset
for row in resultset:
    family_tree[row[0]] = [row[1], row[2], set()]

# Perform query
cur.execute('''SELECT cpr, name_of_disease FROM disease_week02''')

# Getting all rows
resultset = cur.fetchall()

# Close cursor and connection
cur.close()
cnx.close()

import re

for row in resultset:
    if re.search(".*[Cc]ancer.*", row[1]) is None:
        family_tree[row[0]][2].add(row[1])
    else:
        family_tree[row[0]][2].add("Cancer")


def searchTree(key, path = [], child_diseases = None):
    if key is None:
        return set()

    father, mother, diseases = family_tree[key]
    
    if child_diseases is not None:
        diseases = diseases.intersection(child_diseases)
        if not diseases:
            return set()

    new_path = [*path, key]

    if diseases and len(new_path) > 2:
        print(len(new_path), new_path, diseases)
 
    father_diseases = searchTree(father, new_path, diseases)
    mother_diseases = searchTree(mother, new_path, diseases)

    return diseases

    


for key in family_tree.keys():
    searchTree(key)

