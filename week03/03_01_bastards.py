#!/usr/bin/env python3

"""
Who are born out of wedlock? 
Definition: A child is born out of wedlock if the biological father and mother 
is not married when the child is born. In the absence of information, you can 
not claim a child is born out of wedlock (that means if you only know the 
mother from the database, you can not claim the child is a bastard). 
"""
import datetime
import mysql.connector
# Make database connection
cnx = mysql.connector.connect(user='s184260', passwd='OCiZxmrk', db='s184260')

# Create cursor
cur = cnx.cursor()

# Perform query
cur.execute('''SELECT * FROM persons_week02''')

# Getting all rows
resultset = cur.fetchall()

# Compute on resultset
for row in resultset:
    cpr = row[0]
    father_cpr, mother_cpr = row[-2], row[-1]
    if father_cpr is None or mother_cpr is None:
        continue

    #print(row)

    cur.execute('''SELECT * FROM marriage_week02 WHERE male_cpr=%s AND female_cpr=%s''', (father_cpr, mother_cpr))

    # Getting all rows
    resultset = cur.fetchall()

    if len(resultset) == 0:
        continue
    
    y, m, d = int(cpr[4:6]), int(cpr[2:4]), int(cpr[:2])
    century = 2000 if (int(father_cpr[4:6]) > y) or (int(mother_cpr[4:6]) > y) else 1900

    birth_date = datetime.date(century + y, m, d)

    bastard = True

    # Compute on resultset
    for mrow in resultset:
        #print(mrow)
        marriage_start_date, marriage_end_date = mrow[2:4]
        if marriage_start_date < birth_date and (marriage_end_date is None or birth_date < marriage_end_date):
            bastard = False

    if bastard:
        print(row[1], row[2], "("+row[0]+") is a bastard.")
    else:
        print(row[1], row[2], "is not a bastard.")


# Close cursor and connection
cur.close()
cnx.close()
