#!/usr/bin/env python3

import mysql.connector

# Make database connection
cnx = mysql.connector.connect(user='s183493', passwd='Lcy6srAT', db='s183493')


# Create cursor
cur = cnx.cursor()

# Perform query
cur.execute('''SELECT * FROM persons''')

# Getting all rows
personset = cur.fetchall()


def get_diseases(cpr):
    cur.execute('''SELECT name_disease FROM disease WHERE cpr = %s''',(cpr,))

    diseaseset = cur.fetchall()

    disease_set = set()

    for line in diseaseset:
        if "cancer" in line[0] or "Cancer" in line[0]:
            line = "Cancer"
        disease_set.add(line)

    return disease_set

def parent_child_disease_comparison(cpr, parent_cpr):
    parent_disease = get_diseases(parent_cpr)
    child_disease = get_diseases(cpr)

    shared = child_disease.intersection(parent_disease)

    return shared

def grandparents(parent_cpr, parent_child_shared_diseases, cpr):
    cur.execute('''SELECT biological_mother, biological_father FROM persons WHERE cpr = %s''',(parent_cpr,))

    grandparents_set = cur.fetchall()

    for grandparent in grandparents_set:
        shared_diseases1 = None
        shared_diseases2 = None
        gp1 = grandparent[0]
        gp2 = grandparent[1]
        if gp1 != None:
            grandparent_disease1 = get_diseases(gp1)
            shared_diseases1 = parent_child_shared_diseases.intersection(grandparent_disease1)

            if len(shared_diseases1) > 0:
                print(shared_diseases1, cpr, parent_cpr, gp1)

        if gp2 != None:
            grandparent_disease2 = get_diseases(gp2)
            shared_diseases2 = parent_child_shared_diseases.intersection(grandparent_disease2)

            if len(shared_diseases2) > 0:
                print(shared_diseases2, cpr, parent_cpr, gp2)
    return

# Compute on resultset
for row in personset:
    cpr = row[0]
    mother_cpr = row[-2]
    father_cpr = row[-1]

    child_mother = parent_child_disease_comparison(cpr, mother_cpr)
    child_father = parent_child_disease_comparison(cpr, father_cpr)

    if len(child_mother) > 0:
       grandparents(mother_cpr, child_mother, cpr)

    if len(child_father) > 0:
        grandparents(father_cpr, child_father, cpr)

# Close cursor and connection
cur.close()
cnx.close()
