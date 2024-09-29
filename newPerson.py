def getUsers(users_collection):

    # Fetch users from the collection
    try:
        users = list(users_collection.find().limit(100))  # Adjust the projection to match your fields
    except:
        users = list(users_collection.find().limit(50))

    return users