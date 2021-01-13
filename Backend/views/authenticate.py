from flask import Blueprint, request, jsonify, make_response
import jwt
import datetime
from functools import wraps
import bcrypt
from database.db import mongo
import re

authenticate = Blueprint("authenticate", __name__)

secret_key = "mysecret"

"""
Futbase provides multiple methods of authentication and security
    1. User passwords are encrypted with bcrypt
    2. Jwts are used to authenticate on every endpoint
    3, Access levels used to authenticate important endpoints
"""


def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = jwt.decode(token, secret_key)
        except:
            return jsonify({"message": "Token is invalid"}), 401

        bl_token = mongo.db.blacklist.find_one({"token": token})
        if bl_token is not None:
            return make_response(jsonify({"message": "Token has been cancelled"}), 401)
        return func(*args, **kwargs)

    return jwt_required_wrapper


def admin_required(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        token = request.headers["x-access-token"]
        data = jwt.decode(token, secret_key)
        if data["admin"]:
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({"message": "Admin access required"}), 401)

    return admin_required_wrapper


@authenticate.route("/api/v1.0/login", methods=["GET"])
def login():
    email = request.args.get("username")
    password = request.args.get("password")

    if valid_login_credentials(email, password):
        user = mongo.db.users.find_one({"email": email})
        if user is not None:
            if bcrypt.checkpw(bytes(password, "UTF-8"), user["password"]):
                token = jwt.encode(
                    {
                        "email": email,
                        "admin": True if user["user_type"] == "ADMIN" else False,
                        "exp": datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=90),
                    },
                    secret_key,
                )
                return make_response(
                    jsonify(
                        {
                            "token": token.decode("UTF-8"),
                            "email": email,
                            "admin": True if user["user_type"] == "ADMIN" else False,
                            "user_id": str(user["_id"]),
                        }
                    ),
                    200,
                )
            else:
                return make_response(jsonify({"message": "Bad password"}), 400)
        else:
            return make_response(jsonify({"message": "Bad username"}), 400)

    return make_response(
        jsonify({"message": "Username and password required"}),
        400,
    )


@authenticate.route("/api/v1.0/logout", methods=["GET"])
@jwt_required
def logout():
    token = None
    if "x-access-token" in request.headers:
        token = request.headers["x-access-token"]
    if not token:
        return make_response(jsonify({"message": "Token is missing"}), 401)
    else:
        mongo.db.blacklist.insert_one({"token": token})
        return make_response(jsonify({"message": "Logout successful"}), 200)


def valid_login_credentials(email, password):
    if not email or not password:
        return False
    if not re.search(
        "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email
    ) or not mongo.db.users.find_one({"email": email}):
        return False
    if not re.search(
        "^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,15}$", password
    ):
        return False

    return True
