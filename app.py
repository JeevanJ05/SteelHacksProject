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
from newPerson import getUsers 
from google_utils import return10Comparisons
from handleMongoDB import initClient

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Use environment variable for secret key

users_list = [] # global "stack" for matched users w/ current users
seen_users = [] # global "stack" for users we have already seen
mongo_client, users_collection = initClient() # global object for db client and its user collection

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

    global users_list
    global seen_users

    current_user = session.get('user')  # Assuming the current user is stored in the session
    if current_user:
        seen_users.append(current_user['email'])
    
    users_list = return10Comparisons(current_user, users_collection, seen_users)  # Refresh the list with comparisons
    
    # Pass the first 10 users to the frontend
    users_to_display = users_list
    
    # Convert ObjectId to string for safe passing to frontend
    for user in users_to_display:
        user['_id'] = str(user['_id'])
    
    # Remove the first 10 users from the list (they have been "used") and add them to the seen users
    seen_users.extend(users_list)
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
            'socialMedia': request.form['socialMedia'],
            # Handle file upload if necessary
            #'picture': request.files['picture'] if 'picture' in request.files else None
        }

        # Update or insert user preferences in MongoDB
        #if preferences_data['picture']:
            # Convert file to binary or URL as needed; for now, we'll assume it's being saved as URL
            #picture_url = save_picture(preferences_data['picture'])  # Create this function to handle uploads
            #preferences_data['picture'] = picture_url

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

        print(getUsers(users_collection, seen_users))
        return jsonify(getUsers(users_collection, seen_users))





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
    
    