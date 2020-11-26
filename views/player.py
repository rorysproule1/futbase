from flask import Blueprint, Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
import jwt
import datetime
from functools import wraps
import bcrypt
import json
from database.db import mongo

player = Blueprint("player", __name__)

@player.route("/api/v1.0/players", methods=["GET"])
def get_all_players():
    # Get pagination details of the query
    page_num, page_size = 1, 10
    if request.args.get("pn"):
        page_num = int(request.args.get("pn"))
    if request.args.get("ps"):
        page_size = int(request.args.get("ps"))
    page_start = page_size * (page_num - 1)

    # Get all filters for the query
    filters = get_filters(request)

    # Get all players matching query from database
    data_to_return = []
    for player in (
        mongo.db.players.find(filters, get_players_fields(many=True))
        .skip(page_start)
        .limit(page_size)
        .sort("overall", -1)
    ):
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

@player.route("/api/v1.0/players/<string:player_id>", methods=["GET"])
def get_one_player(player_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID"}), 400)

    player = mongo.db.players.find_one({"_id": ObjectId(player_id)})
    if player is not None:
        player["_id"] = str(player["_id"])
        for review in player["reviews"]:
            review["_id"] = str(review["_id"])
        return make_response(jsonify(player), 200)
    else:
        return make_response(jsonify({"error": "No player was found with this ID"}), 404)

# ADD THIS TO POSTMAN ONCE CREATION AND EDITING PLAYERS IS IN PLACE
@player.route("/api/v1.0/players/<string:player_id>", methods=["DELETE"])
def delete_player(player_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID format"}), 400)

    result = mongo.db.players.delete_one({"_id": ObjectId(player_id)})
    if result.deleted_count == 1:
        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"error": "No player found with this ID"}), 404)


def get_filters(request):
    filters = {}
    if request.get_data():
        filters_data = json.loads(request.get_data())["filters"]
        if filters_data.get("name") is not None:
            filters["player_extended_name"] = {
                "$regex": filters_data["name"],
                "$options": "i",
            }
        if filters_data.get("league") is not None:
            filters["league"] = {"$eq": filters_data["league"]}
        if filters_data.get("club") is not None:
            filters["club"] = {"$eq": filters_data["club"]}
        if filters_data.get("nationality") is not None:
            filters["nationality"] = {"$eq": filters_data["nationality"]}
        if filters_data.get("quality") is not None:
            filters["quality"] = {"$eq": filters_data["quality"]}
        if filters_data.get("revision") is not None:
            filters["revision"] = {
                "$regex": filters_data["revision"],
                "$options": "i",
            }
        if filters_data.get("position") is not None:
            if filters_data["position"]:
                filters["position"] = {
                    "$in": get_viable_positions(filters_data["position"])
                }
        if filters_data.get("stats") is not None:
            stats = filters_data["stats"]
            for key in stats:
                filters[key] = {"$gte": stats[key]}
    return filters


def get_viable_positions(position):

    """
    Players in certain positions can have their position modified, so when we search for a particular position,
    it makes sense for us to also search for players that can also play this position with a modifier, giving the user
    as many player options as possible to come to a decision.
    """

    viable_positions = []
    if position in ["GK", "CB"]:
        # these can't be modified
        return [position]
    elif position in ["LB", "LWB"]:
        return ["LB", "LWB"]
    elif position in ["RB", "RWB"]:
        return ["RB", "RWB"]
    elif position in ["RF", "RW", "RM"]:
        return ["RF", "RW", "RM"]
    elif position in ["LF", "LW", "LM"]:
        return ["LF", "LW", "LM"]
    elif position == "CDM":
        return ["CDM", "CM"]
    elif position == "CM":
        return ["CDM", "CM", "CAM"]
    elif position == "CAM":
        return ["CM", "CAM", "CF"]
    elif position == "CF":
        return ["CAM", "CF", "ST"]
    elif position == "ST":
        return ["CF", "ST"]


def get_players_fields(many=False):

    """
    To ensure we are only returning necessary fields from the database, we return a projection
    dependant on if the query is for all players or a specific one.
    """

    if many:
        return {
            "player_name": 1,
            "overall": 1,
            "position": 1,
            "nationality": 1,
            "club": 1,
            "quality": 1,
            "revision": 1,
            "gk_diving": 1,
            "gk_handling": 1,
            "gk_kicking": 1,
            "gk_reflexes": 1,
            "gk_speed": 1,
            "gk_positoning": 1,
            "pace": 1,
            "shooting": 1,
            "passing": 1,
            "dribbling": 1,
            "physicality": 1,
            "defending": 1,
        }

# players.update({}, {"$unset": {"added_date": 1, "intl_rep": 1, "weight": 1, "futbin_id": 1,}}, multi=True)

def valid_id(id):
    return True if ObjectId.is_valid(id) else False
