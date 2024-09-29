def getUsers(users_collection, exclude_users = [], num=10):

    # Fetch users from the collection
    try:
        users = list(users_collection.find({"email": {"$nin": exclude_users}}).limit(num))  # Adjust the projection to match your fields
    except:
        users = list(users_collection.find({"email": {"$nin": exclude_users}}).limit(1))

    return users