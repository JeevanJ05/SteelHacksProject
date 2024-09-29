from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import google_utils
import re
import os
import requests
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode
import json
import secrets
#from newPerson import getUsers 
from google_utils import return10Comparisons, generateAboutMe
from handleMongoDB import initClient

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Use environment variable for secret key

users_list = [] # global "stack" for matched users w/ current users

# Initialize OAuth for Auth0
oauth = OAuth(app)
# Auth0 Configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN').strip('"')
CLIENT_ID = os.getenv('AUTH0_CLIENT_ID').strip('"')
CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET').strip('"')

oauth.register(
    "auth0",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration'
)


mongo_client, users_collection = initClient()

# Routes
@app.route('/')
def index():
    return redirect(url_for('main'))

@app.route('/login')
def login():
    nonce = secrets.token_urlsafe(16)  # Generate a secure nonce
    session['nonce'] = nonce  # Store the nonce in the session
    print("URL", url_for("callback", _external=True))
    
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True),
        nonce=nonce  # Pass the nonce as a parameter
    )

@app.route('/callback')
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        user_info = oauth.auth0.parse_id_token(token, nonce=session['nonce'])  # Pass the nonce
        session["user"] = user_info

        # Prepare user data to be stored
        user_data = {
            "email": user_info["email"],
            "name": user_info["name"],
            "picture": user_info.get("picture"),
            "sub": user_info["sub"],  # This is the unique identifier for the user
        }

        # Check if user already exists in the database
        existing_user = users_collection.find_one({"sub": user_data["sub"]})
        
        if not existing_user:
            # Insert new user into the collection if they do not exist
            users_collection.insert_one(user_data)
            print("New user added to the database:", user_data)
        else:
            print("User already exists in the database:", existing_user)

        return redirect("main")  # Redirect to main after successful login
    except Exception as e:
        print("Error during callback:", e)  # Print error details for debugging
        flash("Login failed. Please try again.")  # Flash message to user
        return redirect(url_for('login'))  # Redirect back to login page




@app.route('/main')
def main():
    # Retrieve 10 users from the database
    #users = getUsers(mongo_client)[:4]  # Limit the number to 10 users

    global users_list
    current_user = session.get('user')  # Assuming the current user is stored in the session
    
    if len(users_list) < 20:  # If we have fewer than 20 users on hand, fetch more
        users_list = return10Comparisons(current_user, mongo_client)  # Refresh the list with comparisons
    
    #users_list = [{'_id': ObjectId('66f868ecf2bbad8477d0f464'), 'email': 'walkershelly@example.org', 'name': 'Christina Walker', 'major': 'Physics', 'interests': ['Movies', 'Photography', 'Music'], 'picture': 'https://dummyimage.com/362x266', 'sub': 'b610b44b-690a-42fe-8cb5-4860ddbe16a0'}, {'_id': ObjectId('66f868ecf2bbad8477d0f451'), 'email': 'nathanielstewart@example.org', 'name': 'Michael Nicholson', 'major': 'Psychology', 'interests': ['Traveling', 'Gaming', 'Photography'], 'picture': 'https://placekitten.com/736/524', 'sub': '5340ab0d-57f5-44e3-ad34-c479896a2024'}, {'_id': ObjectId('66f868eb364c21724a135dba'), 'email': 'john86@example.com', 'name': 'Karen Knight', 'major': 'Biology', 'interests': ['Traveling', 'Reading', 'Music'], 'picture': 'https://placekitten.com/369/633', 'sub': 'f9a9f45b-91b0-48ad-8555-358894450a42'}, {'_id': ObjectId('66f868ecf2bbad8477d0f44d'), 'email': 'victoria98@example.net', 'name': 'Christopher Williams', 'major': 'Engineering', 'interests': ['Reading', 'Photography', 'Sports'], 'picture': 'https://picsum.photos/612/856', 'sub': '1a3c4bef-118d-4558-bbc0-ea39bd783084'}, {'_id': ObjectId('66f868eb364c21724a135db3'), 'email': 'mckinneyandrew@example.com', 'name': 'Scott Schmidt', 'major': 'Economics', 'interests': ['Reading', 'Music', 'Gaming'], 'picture': 'https://placekitten.com/662/856', 'sub': '5cdadf78-5ee1-414f-9cad-2188fdc80469'}, {'_id': ObjectId('66f868eb364c21724a135da0'), 'email': 'jamiemarshall@example.org', 'name': 'Emma Rhodes', 'major': 'Engineering', 'interests': ['Movies', 'Reading', 'Gaming'], 'picture': 'https://placekitten.com/958/694', 'sub': '4ed14060-f454-4a4c-b5ad-cdfb6208f456'}, {'_id': ObjectId('66f868eb364c21724a135df7'), 'email': 'michelle14@example.org', 'name': 'Tanya Jackson', 'major': 'Biology', 'interests': ['Reading', 'Sports', 'Music'], 'picture': 'https://picsum.photos/753/693', 'sub': '4638016d-7c44-4ec3-aa83-7f0abfeca5de'}, {'_id': ObjectId('66f868eb364c21724a135df0'), 'email': 'crystal46@example.net', 'name': 'Andrea Gilbert', 'major': 'Physics', 'interests': ['Photography', 'Gaming', 'Movies'], 'picture': 'https://placekitten.com/776/39', 'sub': '4ba6233a-b9e0-421d-9178-b1965aabad2b'}, {'_id': ObjectId('66f868eb364c21724a135df5'), 'email': 'ssutton@example.net', 'name': 'Melissa Lopez', 'major': 'History', 'interests': ['Music', 'Movies', 'Gaming'], 'picture': 'https://placekitten.com/777/356', 'sub': 'b6849678-b0d8-46ac-83ff-3ab426caf905'}, {'_id': ObjectId('66f868ecf2bbad8477d0f426'), 'email': 'kathleen60@example.net', 'name': 'Nancy Smith', 'major': 'Psychology', 'interests': ['Reading', 'Movies', 'Sports'], 'picture': 'https://dummyimage.com/394x711', 'sub': 'a9987e0f-432f-426e-979b-49ab681364b5'}, {'_id': ObjectId('66f868eb364c21724a135dab'), 'email': 'hillmarisa@example.org', 'name': 'Evan Brown', 'major': 'Economics', 'interests': ['Photography', 'Reading', 'Gaming'], 'picture': 'https://placekitten.com/525/934', 'sub': '5b09ce66-98c9-4241-b5be-7d49550c3ea0'}, {'_id': ObjectId('66f868eb364c21724a135db9'), 'email': 'carolyngibson@example.com', 'name': 'Suzanne Cortez', 'major': 'History', 'interests': ['Music', 'Coding', 'Sports'], 'picture': 'https://placekitten.com/385/145', 'sub': '50dae351-3cd6-4ab6-bdc5-dbe47c869c90'}, {'_id': ObjectId('66f868eb364c21724a135dc5'), 'email': 'escobarwilliam@example.org', 'name': 'Kimberly Buckley', 'major': 'Computer Science', 'interests': ['Movies', 'Sports', 'Coding'], 'picture': 'https://picsum.photos/407/793', 'sub': '0ce386b8-890a-4006-bd58-d955113488c9'}, {'_id': ObjectId('66f868ecf2bbad8477d0f41b'), 'email': 'psmall@example.com', 'name': 'Antonio King', 'major': 'Mathematics', 'interests': ['Movies', 'Photography', 'Sports'], 'picture': 'https://placekitten.com/979/866', 'sub': '11f91e32-ead4-4fb0-8dfc-ec552df042a7'}, {'_id': ObjectId('66f868eb364c21724a135def'), 'email': 'trevor17@example.com', 'name': 'Ian Payne', 'major': 'History', 'interests': ['Gaming', 'Coding', 'Music'], 'picture': 'https://picsum.photos/260/828', 'sub': '58b881c2-74a0-46f0-929e-958bc303051e'}]

    #print(users_list)
    
    # Pass the first 10 users to the frontend
    users_to_display = users_list[:10]
    
    # Convert ObjectId to string for safe passing to frontend
    for user in users_to_display:
        user['_id'] = str(user['_id'])
    
    # Remove the first 10 users from the list (they have been "used")
    users_list = users_list[10:]
    
    return render_template("main.html", users=users_to_display, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(
    f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?" +
    urlencode(
        {
            "returnTo": url_for("main", _external=True),  # Should resolve to the correct URL
            "client_id": os.getenv("AUTH0_CLIENT_ID"),
        },
        quote_via=quote_plus,
        )
    )


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    user_sub = session.get("user", {}).get("sub")  # Get the unique identifier from the session
    
    if request.method == 'POST':
        # Access form data as a dictionary
        preferences_data = {
            'first_name': request.form['firstName'],
            'last_name': request.form['lastName'],
            'major': request.form['major'],
            'interests': request.form['interests'],
            # Handle file upload if necessary
            'picture': request.files['picture'] if 'picture' in request.files else None
        }

        # Update or insert user preferences in MongoDB
        if preferences_data['picture']:
            # Convert file to binary or URL as needed; for now, we'll assume it's being saved as URL
            picture_url = save_picture(preferences_data['picture'])  # Create this function to handle uploads
            preferences_data['picture'] = picture_url

        # Check if user preferences already exist
        existing_user = users_collection.find_one({"sub": user_sub})

        if existing_user:
            # Update user preferences
            users_collection.update_one(
                {"sub": user_sub},
                {"$set": preferences_data}
            )
            print("User preferences updated:", preferences_data)
        else:
            # Insert new user preferences
            preferences_data['sub'] = user_sub  # Ensure sub is included
            users_collection.insert_one(preferences_data)
            print("New user preferences added to the database:", preferences_data)

        return redirect(url_for('main'))

    # If GET request, fetch existing preferences to autofill the form
    user_preferences = users_collection.find_one({"sub": user_sub})
    return render_template("preferences.html", 
                           session=session.get('user'), 
                           pretty=json.dumps(session.get('user'), indent=4),
                           preferences=user_preferences)


@app.route('/load_more_users', methods=['POST'])
def load_more_users():
    if request.method == 'POST':
        # Fetch more users dynamically, this is an example
        # In practice, fetch users from the database, based on some cursor or limit
        more_users = [
            {"name": "Carol", "major": "Biology", "interests": "Genetics", "picture": None},
            {"name": "David", "major": "Mathematics", "interests": "Topology", "picture": None},
            # Add more users as needed
        ]

        return jsonify(more_users)





def save_picture(picture):
    # Example function to save the picture and return a URL or path
    return None
    if picture:
        picture_filename = secure_filename(picture.filename)
        picture_path = os.path.join('static/uploads', picture_filename)
        picture.save(picture_path)
        return f"/static/uploads/{picture_filename}"  # Return the URL for the uploaded picture
    return None

if __name__ == "__main__":
    app.run(debug=True)
    