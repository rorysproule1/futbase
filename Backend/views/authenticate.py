from flask import Blueprint, request, jsonify, make_response
from bson import ObjectId
import jwt
import datetime
from functools import wraps
import bcrypt
from database.db import mongo

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
    auth = request.authorization
    if auth:
        user = mongo.db.users.find_one({"email": auth.username})
        if user is not None:
            if bcrypt.checkpw(bytes(auth.password, "UTF-8"), user["password"]):
                token = jwt.encode(
                    {
                        "email": auth.username,
                        "admin": True if user["user_type"] == "ADMIN" else False,
                        "exp": datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=30),
                    },
                    secret_key,
                )
                return make_response(jsonify({"token": token.decode("UTF-8")}), 200)
            else:
                return make_response(jsonify({"message": "Bad password"}), 401)
        else:
            return make_response(jsonify({"message": "Bad username"}), 401)

    return make_response(
        jsonify({"message": "Authentication required"}),
        401,
        {"WWW-Authenticate": 'Basic realm = "Login required"'},
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
