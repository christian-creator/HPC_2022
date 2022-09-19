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

# Perform query
cur.execute('''SELECT * FROM marriage''')

# Getting all rows
marriageset = cur.fetchall()

# Compute on resultset
for row in personset:
    cpr = row[0]
    mother_cpr = row[-2]
    father_cpr = row[-1]

    if father_cpr == ' ' or mother_cpr == ' ' or father_cpr is None or mother_cpr is None:
        continue

    # Finding the birthday
    year_of_birth = cpr[4:6]
    month_of_birth = cpr[2:4]
    day_of_birth = cpr[:2]

    # Checking which century they are born in
    if father_cpr[4:6] > year_of_birth or mother_cpr[4:6] > year_of_birth:
        century = "20"
    else:
        century = "19"

    updated_birth_date = day_of_birth + month_of_birth + century + year_of_birth

    # Initiating flag marking birth out of wedlock
    wedlock = False

    for mrow in marriageset:
        if mother_cpr == mrow[1] and father_cpr == mrow[0]:
            marriage_start = mrow[2]
            marriage_end = mrow[3]

            if marriage_start < updated_birth_date and (marriage_end is None or marriage_end >= updated_birth_date):
                wedlock = True

    # Printing result
    if wedlock == False:
        print(row[0])

# Close cursor and connection
cur.close()
cnx.close()
