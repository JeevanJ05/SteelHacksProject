import requests
import os
#import newPerson
import google.generativeai as genai
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from newPerson import getUsers
import time

load_dotenv()

API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def generateSocials(name, major, interests):
    try:
        user_prompt = (
            f"Generate me a random social media name for {name} {major} that has {interests}. Make your response one word nothing else and include part of their name."
        )
        try:
            response = model.generate_content(user_prompt)
            return response.text
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

# will generate intersts that alilgn with major and 3 random interests
def generateIntersts(first, last, major, interests):
    try:
        user_prompt = (
            f"Generate 4 semi-random interests for {str(first)} {str(last)} that align with their major but still a little random of {str(major)} and their 3 interests {str(interests)}"
             " in this from [interest 1, interest 2, interest 3, interest 4]. Keep the interest as 2-3 words with no description and no symbols just letters, I"
             " just want their interests like this [interest 1, interest 2, interest 3, interest 4] nothing else"
        )
        try:
            response = model.generate_content(user_prompt)
            return response.text
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

# Function to compare two people based on their interests and majors
def compare_two_people(user1, user2):
    try:
        user_prompt = (
            f"Person 1: {str(user1)} | Person 2: {str(user2)} | "
            "Tell me if these two people have close interests, "
            "don't go into detail! Just see if the interests provided are similar in some way! "
            "Think about it as if you were recommending two people to start a friendship."
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

def return10Comparisons(currentUser, users_collection, exclude_users = []): # returns a list of users that "match"
    users_list = getUsers(users_collection, exclude_users) # gets 10 users by default
    result = []

    for user in users_list:
        if compare_two_people(currentUser, user) == True:

            result.append(user)


    
 
    return result


def generateAboutMe(user):
    try:
        user_prompt = "Generate a short about me from my perspective based on these descriptions in one paragraph", str(user['first_name']), str(user['last_name']), str(user['major']), str(user['interests'])
        try:
            response = model.generate_content(user_prompt)
            print(response.text)
        except Exception as e:
            print(e)
    except Exception as e:
        print("error whoopsie", e)
    pass