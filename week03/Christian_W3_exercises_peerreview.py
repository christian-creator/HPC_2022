
################################################
################## Exercise 1 ##################
################################################

import mysql.connector
import sys
### Query the SQL database
cnx = mysql.connector.connect(user='s165476', passwd='I9DP6nOL', db='s165476', host='localhost')
# Create cursor
cur = cnx.cursor()

# Perform query
cur.execute('''SELECT * FROM person''')
# Getting all rows
person_database = cur.fetchall()

# Perform query
cur.execute('''SELECT * FROM marriage''')
# Getting all rows
marriage_database = cur.fetchall()
cur.close()
cnx.close()

def check_bastard(birthday_person,date_wedding_start,date_wedding_end):
    """Given a date of birth and the start date and end date of the parents wedding check whether the person is a bastard.

    Args:
        birthday_person (str): Date of birth in the format: 'day''month''year'
        date_wedding_start (str): Date wedding day in the format: 'day''month''year'
        date_wedding_end (_type_): Date where the wedding ended in the format_ 'day''month''year'

    Returns:
        _type_: _description_
    """
    # Reformat the dates to integers with the format 'year''month''day'
    birthday_person_format_int = int(birthday_person[4:] + birthday_person[2:4] + birthday_person[0:2])
    date_weeding_start_int = int(date_wedding_start[4:] + date_wedding_start[2:4] + date_wedding_start[0:2])
    if date_wedding_end != '':
        date_weeding_end_int = int(date_wedding_end[4:] + date_wedding_end[2:4] + date_wedding_end[0:2])
        # Check if the birthday is within the range of wedding
        return birthday_person_format_int <= date_weeding_start_int or birthday_person_format_int >= date_weeding_end_int
    else:
        # Check if the birthday is within the range of wedding
        return birthday_person_format_int <= date_weeding_start_int


# Iterate over the person database 
for person in person_database:
    bastard_flag = False
    # Get the CPR-numbers 
    mother_cpr = person[5]
    father_cpr = person[6]
    person_cpr = person[0]

    ### CHANGE: see reason below.
    if father_cpr in (None, "") or mother_cpr in (None, ""):
        continue

    # Calculate century of birthyear from cpr. 
    # If the child has a birthyear lower than their parents the child is from the 2000 otherwise they are from 1900
    centrury_person = 20 if person_cpr[4:6] <= father_cpr[4:6] or person_cpr[4:6] <= father_cpr[4:6] else 19
    # Get birthday in format day+month+year
    birthday_person = person_cpr[0:4] + str(centrury_person) + person_cpr[4:6]

    # If the person has no registered parents the person is considered a bastard.
    #if father_cpr == '' or mother_cpr == '':
        ### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ### This is not what the task says - these people should not be considered bastards.
        ### I moved this up and changed the logic to skip these persons.
        #bastard_flag == True
    
    # Find the parents marriage by filtering the marriage_database by CPR numbers.
    marriages = list(filter(lambda marriage: marriage[0] == father_cpr and  marriage[1] == mother_cpr,marriage_database))
    # If the marraige is found in the database check if the child is a bastard
    if len(marriages) > 0:
        # Get the dates of the wedding start and end. 
        marriage = marriages[0]
        wedding_start = marriage[2]
        wedding_end = marriage[3]
        # Check if birthday falls within the marriage dates
        bastard = check_bastard(birthday_person,wedding_start,wedding_end)
        if bastard:
            bastard_flag = True
    # If the marraige is not found in the database the person is considered a bastard
    else:
        bastard_flag = True

    if bastard_flag:
        print(person)

# In general: vewy niiiice solution


################################################
################## Exercise 2 ##################
################################################

import mysql.connector
import sys
import sys

# Gettting data from the SQL-database
cnx = mysql.connector.connect(user='s165476', passwd='I9DP6nOL', db='s165476', host='localhost')
# Create cursor
cur = cnx.cursor()

# Perform query
cur.execute('''SELECT * FROM person''')
# Getting all rows
person_database = cur.fetchall()
# Perform query
cur.execute('''SELECT * FROM diseases''')
# Getting all rows
disease_database = cur.fetchall()
cur.close()
cnx.close()


def get_diseases_names(diseases):
    """From the diseases database retrieve all of the disease names and rename all cancer diseseases subypes to "Cancer"

    Args:
        diseases (list(tuples)): The disease database retrieved from the mysql database

    Returns:
        list: List of diseasese names
    """
    disease_names = []
    for disease in diseases:
        name = disease[1]
        if "cancer" in name.lower(): ### This is much better than my regex.
            disease_names.append("Cancer")
        else:
            disease_names.append(name)
        
        # No Cancer renaming
        # disease_names.append(name)
    return disease_names


def get_parents(person_database,person_cpr):
    """From a person_CPR number retrieve the person-database entries of the parents.

    Args:
        person_database (list(tuples)): Person database retrieved from the SQL-database
        person_cpr (str): CPR-number of the child

    Returns:
        tuple, tuple: Database entry of dad, Database entry of mom.
    """
    # Get the person datbase entry from the child's CPR
    query = list(filter(lambda person: person[0] == person_cpr,person_database))
    if len(query) > 0:
        child = query[0]
        mother = child[5]
        father = child[6]
        return father, mother
    else:
        return '',''

def get_disease_heritage(person_database,father,mother,disease,cprs_w_disease):
    """Calculate the longest disease heritage from a seed. 
       get_disease_heritage() is based on recursion meaning that it is called within the function.

    Args:
        person_database (list(tuples)): The person database retrieved from the SQL-database
        father (str): CPR of father
        mother (str): CPR of mother
        disease (str): The name of the disease
        cprs_w_disease (list): The cprs in the heritage which has the disease

    Returns:
        list: The cprs in the heritage which has the disease
    """
    # Get the disease names of the parents
    disease_names_father = get_diseases_names(filter(lambda x: x[0] == father, disease_database))
    disease_names_mother = get_diseases_names(filter(lambda x: x[0] == mother, disease_database))

    # If the dad has the disease add his CPR to the list of cprs_w_disease. Then retrieve his parents and call the function get_disease_heritage again.
    if disease in disease_names_father and disease not in disease_names_mother:
        cprs_w_disease.append(father)
        father,mother = get_parents(person_database,father)
        return get_disease_heritage(person_database,father,mother,disease,cprs_w_disease)
    
    # If the mom has the disease add her CPR to the list of cprs_w_disease. Then retrieve her parents and call the function get_disease_heritage again.
    elif disease not in disease_names_father and disease in disease_names_mother:
        cprs_w_disease.append(mother)
        father,mother = get_parents(person_database,mother)
        return get_disease_heritage(person_database,father,mother,disease,cprs_w_disease)
    
    # If both the mom and the dad has the disease find the longest heritage line of the disease and add to the  
    elif disease in disease_names_father and disease in disease_names_mother:
        # Get the parents of the parents
        mothers_father,mothers_mother = get_parents(person_database,mother)
        fathers_father,fathers_mother = get_parents(person_database,father)
        # Calcualte the heritage lnes
        mother_branch = get_disease_heritage(person_database,mothers_father,mothers_mother,disease,cprs_w_disease + [mother])
        father_branch = get_disease_heritage(person_database,fathers_father,fathers_mother,disease,cprs_w_disease + [father])
        # Find the longest
        max_len = max((len(mother_branch),len(father_branch)))
        max_index = (len(mother_branch),len(father_branch)).index(max_len)
        return (mother_branch,father_branch)[max_index]

    else:
        #return cpr_w_disease
        ### Lol stavefejl
        return cprs_w_disease


# Try all people as the seed with all diseases as the seed.
for person in person_database:
    seed_person_cpr = person[0]
    # Get the diseases of the person
    diseases = list(filter(lambda x: x[0] == person[0], disease_database))
    disease_names = get_diseases_names(diseases)
    father,mother = get_parents(person_database,seed_person_cpr)
    # If the person has a disease calcuate the disease heritage
    if len(diseases) > 0:
        for seed_disease in set(disease_names):
            cpr_w_disease = get_disease_heritage(person_database,father, mother, seed_disease,[seed_person_cpr])
            if len(cpr_w_disease) >= 3:
                print("-"*100)
                print(seed_disease,seed_person_cpr)
                print(len(cpr_w_disease),seed_person_cpr,seed_disease,cpr_w_disease)
                print("-"*100)

### Ja, altså, det er umiddelbart fint, men giver tilsyneladende maks kun een løsning
### per seed. Fx har 051294-8574's forældre begge den samme far (yikes), der også havde 
### cancer (endnu mere yikes), så der er flere paths du ikke viser (stakkels Sanne).

