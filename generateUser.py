import random
from faker import Faker
import json

from handleMongoDB import initClient
from fakeUserData import majors, interests
from google_utils import generateIntersts, generateSocials

# init faker
fake = Faker()

# connect to db and init client and get users collection
mongo_client, users_collection = initClient()

def generateStudentData():
    first_name = fake.first_name()
    middle_name = fake.first_name()
    last_name = fake.last_name()

    # Generate email (FirstInitialMiddleInitialLastInitial123@pitt.edu)
    email = f"{first_name[0].lower()}{middle_name[0].lower()}{last_name[0].lower()}{random.randint(100, 999)}@pitt.edu"

    # Generate random major and interests
    major = random.choice(majors)

    # Randomly select 3 interests
    sampled_interests = random.sample(interests, min(3, len(interests)))
    
    # Call generateIntersts and print debug information
    interest = generateIntersts(first_name, last_name, major, sampled_interests)
    print("Generated interests from generateIntersts:", interest)

    # Directly assign the interest if it is a list
    interests_list = str(interest)

    # Debug print for interests_list
    print("Final interests list:", interests_list)  # Check the final interests list

    # Generate social
    social = generateSocials(first_name, major, interests_list)

    # Check if social is None and set to an empty string if it is
    if social is None:
        social = ''

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "major": major,
        "interests": interests_list,  # Directly use the interests list
        "socialMedia": social.strip()  # Use the cleaned-up social string
    }




def populate_database(num_students):
    student_data_list = []  # Create a list to hold all student data
    
    for _ in range(num_students):
        person = generateStudentData()
        print(person)

        student_data_list.append(person)  # Append the generated person to the list

    # Insert all student data at once
    if student_data_list:
        users_collection.insert_many(student_data_list)

    print("Inserted", len(student_data_list), "students into the database.")