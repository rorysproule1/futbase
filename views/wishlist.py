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


wishlist = Blueprint("wishlist", __name__)


@wishlist.route("/api/v1.0/users/<string:user_id>/wishlist", methods=["GET"])
def get_user_wishlist(user_id):
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID"}), 400)

    data_to_return = []
    user = mongo.db.users.find_one(
        {"_id": ObjectId(user_id)}, {"wishlist": 1, "_id": 0}
    )
    for player in user["wishlist"]:
        player["_id"] = str(player["_id"])
        data_to_return.append(player)

    return make_response(jsonify(data_to_return), 200)


@wishlist.route("/api/v1.0/users/<string:user_id>/wishlist", methods=["POST"])
def add_player_to_wishlist(user_id):
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID format"}), 400)

    if not valid_wishlist_data(request.form):
        return make_response(jsonify({"error": "Invalid wishlist data"}), 400)

    wishlist_player = {
        "_id": ObjectId(),
        "player_id": request.form["player_id"],
        "base_id": int(request.form["base_id"]),
    }
    mongo.db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$push": {"wishlist": wishlist_player}}
    )

    return make_response(
        jsonify({"wishlist_player_id": str(wishlist_player["_id"])}), 201
    )


@wishlist.route(
    "/api/v1.0/users/<string:user_id>/wishlist/<string:wishlist_id>", methods=["DELETE"]
)
def delete_player_from_wishlist(user_id, wishlist_id):
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID format"}), 400)
    if not valid_id(wishlist_id):
        return make_response(jsonify({"error": "Invalid wishlist ID format"}), 400)

    mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"wishlist": {"_id": ObjectId(wishlist_id)}}},
    )

    return make_response(jsonify({}), 204)


def valid_id(id):
    return True if ObjectId.is_valid(id) else False


def valid_wishlist_data(post_data):
    player_id = post_data.get("player_id")
    base_id = post_data.get("base_id")

    if player_id and base_id:
        # ensure the player looking to be added exists and that the base version provided also exists
        wishist_player = mongo.db.players.find_one({"_id": ObjectId(player_id)})
        base_player = mongo.db.players.find({"resource_id": base_id})

        if wishist_player is not None and base_player is not None:
            return True

    return False
