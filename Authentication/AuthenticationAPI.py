from db import *
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS, cross_origin
import os
import sys
import jwt
import datetime
import pymongo
from functools import wraps
from flask import Blueprint
from flask import current_app
sys.path.append("../db")

authentication_api = Blueprint("authentication", __name__)

# Uncomment the create_index command if you need to recreate the expiration index for Session collection
# https://stackoverflow.com/questions/54750273/pymongo-and-ttl-wrong-expiration-time
# db.Session.create_index("createdAt", expireAfterSeconds = 120)

"""
Decorative function: 
checks for and verifies token. Used in /protected
"""


def check_for_token(token, username):
    # if request does not have a token
    if not token:
        return False

    # verify the user
    try:
        data = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=["HS256"])
        currentUser = db.User.find_one(
            {'userID': data['userID'], 'passwordHash': data['passwordHash']})
        currentUsername = currentUser['userID']

        # If username supplied,
        if username and username != currentUsername and currentUsername != "RH_JCRC":
            raise Exception("Wrong UserID")
    except Exception as e:
        print(e)
        return False

    # check if token has expired (compare time now with createdAt field in document + timedelta)
    originalToken = db.Session.find_one(
        {'userID': data['userID'], 'passwordHash': data['passwordHash']})
    oldTime = originalToken['createdAt']
    # print(datetime.datetime.now())
    # print(oldTime)
    if datetime.datetime.now() > oldTime + datetime.timedelta(minutes=2):
        return False

    # recreate session (with createdAt updated to now)
    #db.Session.remove({'userID': { "$in": data['username']}, 'passwordHash': {"$in": data['passwordHash']}})
    #db.Session.insert_one({'userID': data['username'], 'passwordHash': data['passwordHash'], 'createdAt': datetime.datetime.now()})
    db.Session.update({'userID': data['userID'], 'passwordHash': data['passwordHash']}, {
        '$set': {'createdAt': datetime.datetime.now()}}, upsert=True)
    return True


"""
Register route:
Within POST request, obtain userID, password and email and add to User table in Mongo, if userID has not been registered previously
If successful return 200, else return 500
"""


@authentication_api.route('/register', methods=['POST'])
def register():
    try:
        # extract userID, password and email
        formData = request.get_json()
        userID = formData["userID"]
        passwordHash = formData["passwordHash"]
        email = formData["email"]
        position = formData["position"]
        displayName = formData["displayName"]
        bio = formData["bio"]
        block = formData["block"]
        telegramHandle = formData["telegramHandle"]
        if db.User.find({'userID': userID}).count():  # entry exists
            return jsonify({'message': 'User already exists'}), 401
        # add to User table
        # note: if the user data does not adhere to defined validation standards, an error will be thrown here
        db.User.insert_one({"userID": userID,
                            "passwordHash": passwordHash,
                            "email": email,
                            "position": position
                            })
        db.Profiles.insert_one({"userID": userID,
                               "displayName": displayName,
                                "bio": bio,
                                "block": block,
                                "telegramHandle": telegramHandle,
                                "profilePictureURI": "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=identicon"
                                })
    except Exception as e:
        return jsonify({'message': 'An error was encountered.'}), 500
    return jsonify({'message': 'User successfully created!'}), 200


"""
Login route:
Within POST request, verify userID and passwordHash are valid.
If true, create session, return JWT to client, else return 500.
"""


@authentication_api.route('/login', methods=['POST'])
def login():
    req = request.get_json()
    userID = req['userID']
    passwordHash = req['passwordHash']
    # authenticate the credentials
    if not db.User.find({'userID': userID, 'passwordHash': passwordHash}).limit(1):
        return jsonify({'message': 'Invalid credentials'}), 403
    # insert new session into Session table
    #db.Session.createIndex({'createdAt': 1}, { expireAfterSeconds: 120 })
    db.Session.update({'userID': userID, 'passwordHash': passwordHash}, {'$set': {
                      'userID': userID, 'passwordHash': passwordHash, 'createdAt': datetime.datetime.now()}}, upsert=True)
    #db.Session.update({'userID': username, 'passwordHash': passwordHash}, {'$set': {'createdAt': datetime.datetime.now()}}, upsert=True)
    # generate JWT (note need to install PyJWT https://stackoverflow.com/questions/33198428/jwt-module-object-has-no-attribute-encode)
    token = jwt.encode({'userID': userID,
                        'passwordHash': passwordHash  # to change timedelta to 15 minutes in production
                        }, current_app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token}), 200


"""
Protected route:
Acts as gatekeeper; can only access requested resource if you are authenticated ie valid session
Successful authentication will return the 200 status code below. Any other errors will be as reflected in the wrapper function.
"""


@authentication_api.route('/protected', methods=['GET'])
# @check_for_token
def protected(currentUser):
    return jsonify({'message': 'Successfully logged in. Redirecting.'}), 200


"""
Logout route:
Delete the session entry
"""


@authentication_api.route('/logout', methods=['GET'])
def logout():
    userID = request.args.get('userID')
    try:
        db.Session.remove({"userID": userID})
    except:
        return jsonify({'message': 'An error occurred'}), 500
    return jsonify({'message': 'You have been successfully logged out'}), 200
