from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
import jwt
import datetime
from functools import wraps
import bcrypt
import json

app = Flask(__name__)
client = MongoClient("mongodb://127.0.0.1:27017")

db = client.futbase
players = db.players

app.config["SECRET_KEY"] = "mysecret"

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/api/v1.0/players", methods=["GET"])
def show_all_players():
    # Get pagination details of query
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
    projected_fields = get_players_fields(many=True)
    for player in (
        players.find(filters, projected_fields).skip(page_start).limit(page_size).sort("overall", -1)
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

    if not data_to_return:
        return make_response(
            jsonify({"error": "No players matched the given search criteria"}), 404
        )

    return make_response(jsonify(data_to_return), 200)


def get_filters(request):
    filters = {}
    filter_data = request.get_data()
    if filter_data:
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
        if filters_data.get("position") is not None:
            if filters_data["position"]:
                filters["position"] = {
                    "$in": get_viable_positions(filters_data["position"])
                }
    return filters


def get_viable_positions(position):
    viable_positions = []
    if position in ["GK", "CB"]:
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
        return [
            "CF",
            "ST",
        ]


def get_players_fields(many=False):
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