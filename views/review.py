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


review = Blueprint("review", __name__)


@review.route("/api/v1.0/players/<string:player_id>/review", methods=["GET"])
def get_player_reviews(player_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID"}), 400)

    data_to_return = []
    user = mongo.db.users.find_one(
        {"_id": ObjectId(player_id)}, {"review": 1, "_id": 0}
    )
    for player in user["review"]:
        player["_id"] = str(player["_id"])
        data_to_return.append(player)

    return make_response(jsonify(data_to_return), 200)


@review.route("/api/v1.0/players/<string:player_id>/add", methods=["POST"])
def test(player_id):

    data_to_return = []
    for player in mongo.db.players.find():
        # Append relevant data for each player
        data_to_return.append(
            {
                "player_id": str(player["_id"]),
                "name": player["player_name"],
                "overall": player["overall"],
                "position": player["position"],
                "nationality": player["nationality"],
                "club": player["club"],
                "quality": player["quality"],
                "revision": player["revision"],
                # stats stored are dependant on if the player is a goalkeeper or outfield player
                "stats": {
                    "diving": player["gk_diving"],
                    "handling": player["gk_handling"],
                    "kicking": player["gk_kicking"],
                    "reflexes": player["gk_reflexes"],
                    "speed": player["gk_speed"],
                    "positioning": player["gk_positoning"],
                }
                if player["position"] == "GK"
                else {
                    "pace": player["pace"],
                    "shooting": player["shooting"],
                    "passing": player["passing"],
                    "dribbling": player["dribbling"],
                    "physical": player["physicality"],
                    "defending": player["defending"],
                },
            }
        )
    return make_response(jsonify(data_to_return), 200)


# @wishlist.route("/api/v1.0/users/<string:user_id>/wishlist", methods=["POST"])
# def add_player_to_wishlist(user_id):
#     if not valid_id(user_id):
#         return make_response(jsonify({"error": "Invalid user ID format"}), 400)

#     if not valid_wishlist_data(request.form):
#         return make_response(jsonify({"error": "Invalid wishlist data"}), 400)

#     wishlist_player = {
#         "_id": ObjectId(),
#         "player_id": request.form["player_id"],
#         "base_id": int(request.form["base_id"]),
#     }
#     mongo.db.users.update_one(
#         {"_id": ObjectId(user_id)}, {"$push": {"wishlist": wishlist_player}}
#     )

#     return make_response(
#         jsonify({"wishlist_player_id": str(wishlist_player["_id"])}), 201
#     )


# @wishlist.route(
#     "/api/v1.0/users/<string:user_id>/wishlist/<string:wishlist_id>", methods=["DELETE"]
# )
# def delete_player_from_wishlist(user_id, wishlist_id):
#     if not valid_id(user_id):
#         return make_response(jsonify({"error": "Invalid user ID format"}), 400)
#     if not valid_id(wishlist_id):
#         return make_response(jsonify({"error": "Invalid wishlist ID format"}), 400)

#     mongo.db.users.update_one(
#         {"_id": ObjectId(user_id)},
#         {"$pull": {"wishlist": {"_id": ObjectId(wishlist_id)}}},
#     )

#     return make_response(jsonify({}), 204)


def valid_id(id):
    return True if ObjectId.is_valid(id) else False