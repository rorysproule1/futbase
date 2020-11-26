from flask import Blueprint, Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
import jwt
import datetime
from functools import wraps
import bcrypt
import json
from database.db import mongo
import re


user = Blueprint("user", __name__)


@user.route("/api/v1.0/users/<string:user_id>", methods=["GET"])
def get_user(user_id):
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID"}), 400)

    player = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if player is not None:
        player["_id"] = str(player["_id"])
        return make_response(jsonify(player), 200)
    else:
        return make_response(jsonify({"error": "No user was found with this ID"}), 404)


@user.route("/api/v1.0/users", methods=["POST"])
def add_user():
    if valid_post_user(request.form):
        new_user = {
            "email": request.form["email"],
            "password": request.form["password"],
            "user_type": "USER",
            "platform": request.form["platform"],
            "wishlist": [],
        }
        new_user_id = mongo.db.users.insert_one(new_user)
        return make_response(jsonify({"user_id": str(new_user_id.inserted_id)}), 201)
    else:
        return make_response(jsonify({"error": "Missing or invalid user data"}), 404)

@user.route("/api/v1.0/users/<string:user_id>", methods=["PUT"])
def edit_user(user_id):
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID format"}), 400)

    put_data = {}
    for key in request.form:
        put_data[key] = request.form[key]

    if valid_put_user(request.form):
        result = mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": put_data
            },
        )
    else:
        return make_response(jsonify({"error": "Missing or invalid user data"}), 404)

    if result.matched_count == 1:
        return make_response(jsonify({"user_id": user_id}), 200)
    else:
        return make_response(jsonify({"error": "Invalid user ID"}), 404)

@user.route("/api/v1.0/users/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID format"}), 400)

    result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"error": "No user found with this ID"}), 404)


def valid_id(id):
    return True if ObjectId.is_valid(id) else False


def valid_post_user(user):

    if "email" in user and "password" in user and "platform" in user:
        if (
            re.search("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$", user["email"])
            and re.search(
                # Password must contain 8-15 characters, with at least 1 number and special character
                "^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,15}$", user["password"]
            )
            and user["platform"] in ["XBOX", "PC", "PS"]
        ):
            return True

    return False

def valid_put_user(user):

    if "email" in user:
        if not re.search("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$", user["email"]):
            return False
    if "password" in user:
        if not re.search("^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,15}$", user["password"]):
            return False
    if "platform" in user:
        if user["platform"] not in ["XBOX", "PC", "PS"]:
            return False

    return True
