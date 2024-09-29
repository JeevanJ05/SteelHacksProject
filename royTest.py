from handleMongoDB import initClient
from newPerson import getUsers
from google_utils import generateAboutMe

mongo_client, users_collection = initClient()

generateAboutMe(getUsers(users_collection)[3])