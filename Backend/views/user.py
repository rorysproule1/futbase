from flask import Blueprint, request, jsonify, make_response
from bson import ObjectId
import bcrypt
from database.db import mongo
import re
from views.authenticate import jwt_required
from views.email import send_registration_email, send_deletion_email


user = Blueprint("user", __name__)

"""
The following endpoints provide functionality to handle interactions with the
user logged in or attempting to log in. 
"""


@user.route("/api/v1.0/users/<string:user_id>", methods=["GET"])
@jwt_required
def get_user(user_id):
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID"}), 400)
    player = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if player is not None:
        player["_id"] = str(player["_id"])
        player["password"] = str(player["password"])
        return make_response(jsonify(player), 200)
    else:
        return make_response(jsonify({"error": "No user was found with this ID"}), 404)


@user.route("/api/v1.0/users", methods=["POST"])
def add_user():
    if valid_post_user(request.form):
        # Encrypt user's password before storing
        byte_password = request.form["password"].encode()
        encrypted_password = bcrypt.hashpw(byte_password, bcrypt.gensalt())

        new_user = {
            "email": request.form["email"],
            "password": encrypted_password,
            "user_type": request.form["user_type"],
            "wishlist": [],
        }
        new_user_id = mongo.db.users.insert_one(new_user)

        # Send welcome email
        send_registration_email(request.form["email"])

        return make_response(jsonify({"user_id": str(new_user_id.inserted_id)}), 201)
    else:
        return make_response(jsonify({"error": "Missing or invalid user data"}), 404)


@user.route("/api/v1.0/users/<string:user_id>", methods=["PUT"])
@jwt_required
def edit_user(user_id):
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID format"}), 400)

    put_data = {}
    for key in request.form:
        put_data[key] = request.form[key]

    if valid_put_user(request.form):
        result = mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": put_data},
        )
    else:
        return make_response(jsonify({"error": "Missing or invalid user data"}), 404)

    if result.matched_count == 1:
        return make_response(jsonify({"user_id": user_id}), 200)
    else:
        return make_response(jsonify({"error": "Invalid user ID"}), 404)


@user.route("/api/v1.0/users/<string:user_id>", methods=["DELETE"])
@jwt_required
def delete_user(user_id):
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID format"}), 400)

    # get user's email address before deleting for use later
    email = mongo.db.users.find_one({"_id": ObjectId(user_id)}, {"email": 1})["email"]

    result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        # If account was deleted, send email confirming so
        send_deletion_email(email)
        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"error": "No user found with this ID"}), 404)


def valid_id(id):
    return True if ObjectId.is_valid(id) else False


def valid_post_user(user):

    if (
        "email" in user
        and "password" in user
        and "user_type" in user
    ):
        if (
            re.search(
                "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", user["email"]
            )
            and re.search(
                # Password must contain 8-15 characters, with at least 1 number and special character
                "^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,15}$",
                user["password"],
            )
            and user["user_type"] in ["ADMIN", "USER"]
            and not mongo.db.users.find_one({"email": user["email"]})
        ):
            return True

    return False


def valid_put_user(user):

    if "email" in user:
        if not re.search(
            "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", user["email"]
        ) or not mongo.db.users.find_one({"email": user["email"]}):
            return False
    if "password" in user:
        if not re.search(
            "^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,15}$",
            user["password"],
        ):
            return False
    if "user_type" in user:
        if user["user_type"] not in ["ADMIN", "USER"]:
            return False

    return True
