from flask import Blueprint, Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
import jwt
import datetime
from functools import wraps
import bcrypt
import json
from database.db import mongo


user = Blueprint("user", __name__)


@user.route("/api/v1.0/users/<string:id>", methods=["GET"])
def get_user(id):
    if not valid_id(id):
        return make_response(jsonify({"error": "Invalid user ID"}), 400)

    player = mongo.db.users.find_one({"_id": ObjectId(id)})
    if player is not None:
        player["_id"] = str(player["_id"])
        return make_response(jsonify(player), 200)
    else:
        return make_response(jsonify({"error": "No user was found with this ID"}), 404)

@user.route("/api/v1.0/users", methods=["POST"])
def add_user():
    if valid_user(request.form):
        new_user = {
            "email": request.form["email"],
            "password": request.form["password"],
            "user_type": "USER",
            "platform": request.form["platform"],
            "wishlist": [],
            "reviews": []
        }
        new_user_id = mongo.db.users.insert_one(new_user)
        return make_response(jsonify({"user_id": str(new_user_id.inserted_id)}), 201)
    else:
        return make_response(jsonify({"error": "Missing form data"}), 404)

def valid_id(id):
    if ObjectId.is_valid(id):
        return True
    else:
        return False

def valid_user(user):
    if "email" in user and "password" in user and "platform" in user:
        return True
    else:
        return False
