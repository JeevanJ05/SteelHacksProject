import requests
import os
#import newPerson
import google.generativeai as genai
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
#from newPerson import getUsers
import time

load_dotenv()

API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# Function to retrieve 100 users from MongoDB
def get_10_users(mongo_client):
    if mongo_client:
        users_collection = mongo_client['Pitt_Students']['users']  # Ensure this matches your MongoDB database
    else:
        raise Exception("MongoDB connection failed. Check your connection settings.")

    return list(users_collection.aggregate([{"$sample": {"size": 10}}]))


# Function to compare two people based on their interests and majors
def compare_two_people(user1, user2):
    try:
        user_prompt = (
            f"Person 1: {str(user1)} | Person 2: {str(user2)} | "
            "Tell me if these two people have close interests, "
            "don't go into detail! Just see if the interests provided are similar in some way! "
            "Think about it as an average of 1/2, if i were to give you 10 people, 5 would be matches"
            "Also, if they have a similar major, let me know! "
            "If either of those are true, ouput 'true' and only 'true' please!"
        )

        try:
            response = model.generate_content(user_prompt)
            if response.text.strip().lower() == "true":
                return True
            else:
                print("Not similar.")
        except Exception as e:
            print(f"An error occurred with the model: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage

def return10Comparisons(currentUser, mongo_client): # returns a list of users that "match"
    users_list = get_10_users(mongo_client)
    result = []

    for user in users_list:
        if compare_two_people(currentUser, user) == True:
            result.append(user)
 
    return result


def generateAboutMe(user):
    try:
        user_prompt = "Generate a short about me from my perspective based on these descriptions in one paragraph", str(user['name']), str(user['major']), str(user['interests'])
        try:
            response = model.generate_content(user_prompt)
            print(response.text)
        except Exception as e:
            print(e)
    except Exception as e:
        print("error whoopsie", e)
    pass

#generateAboutMe(getUsers(mongo_client)[1])