from flask import Blueprint, request, jsonify, make_response
from bson import ObjectId
import json
from database.db import mongo
from views.authenticate import jwt_required, admin_required
from views.email import send_wishlist_email

player = Blueprint("player", __name__)


@player.route("/api/v1.0/players", methods=["GET"])
# @jwt_required
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
    player_list = (
        mongo.db.players.find(filters, get_players_fields(many=True))
        .skip(page_start)
        .limit(page_size)
        .sort("overall", -1)
    )
    data_to_return = [{"player_count": player_list.count()}]
    for player in player_list:
        # Append relevant data for each player
        data_to_return.append(
            {
                "player_id": str(player["_id"]),
                "name": player["player_name"],
                "overall": player["overall"],
                "position": player["position"],
                "nationality": player["nationality"],
                "league": player["league"],
                "club": player["club"],
                "quality": player["quality"],
                "revision": player["revision"],
                # Stats stored are dependant on if the player is a goalkeeper or outfield player
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


@player.route("/api/v1.0/test", methods=["POST"])
# @jwt_required
def test_get_all_players():
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
    player_list = (
        mongo.db.players.find(filters, get_players_fields(many=True))
        .skip(page_start)
        .limit(page_size)
        .sort("overall", -1)
    )
    data_to_return = [{"player_count": player_list.count()}]
    for player in player_list:
        # Append relevant data for each player
        data_to_return.append(
            {
                "player_id": str(player["_id"]),
                "name": player["player_name"],
                "overall": player["overall"],
                "position": player["position"],
                "nationality": player["nationality"],
                "league": player["league"],
                "club": player["club"],
                "quality": player["quality"],
                "revision": player["revision"],
                # Stats stored are dependant on if the player is a goalkeeper or outfield player
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
# @jwt_required
def get_one_player(player_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID"}), 400)

    player = mongo.db.players.find_one(
        {"_id": ObjectId(player_id)}, get_players_fields(request.args.get("many"))
    )
    if player is not None:
        player["_id"] = str(player["_id"])
        if player.get("reviews"):
            for review in player["reviews"]:
                review["_id"] = str(review["_id"])
        return make_response(jsonify(player), 200)
    else:
        return make_response(
            jsonify({"error": "No player was found with this ID"}), 404
        )


@player.route("/api/v1.0/players", methods=["POST"])
@jwt_required
@admin_required
def add_player():
    if valid_post_player(request.form):
        new_player = {
            # General Info
            "player_name": request.form.get("player_name"),
            "player_extended_name": request.form.get("player_extended_name"),
            "overall": int(request.form.get("overall")),
            "quality": request.form.get("quality"),
            "revision": request.form["revision"],
            "origin": request.form.get("origin"),
            "height": int(request.form.get("height")),
            "nationality": request.form.get("nationality"),
            "league": request.form.get("league"),
            "club": request.form.get("club"),
            "position": request.form.get("position"),
            "base_id": int(request.form.get("base_id")),
            "pref_foot": request.form.get("pref_foot"),
            "att_workrate": request.form.get("att_workrate"),
            "def_workrate": request.form.get("def_workrate"),
            "skill_moves": int(request.form.get("skill_moves")),
            "weak_foot": int(request.form.get("weak_foot")),
            # Prices
            "pc_last": request.form.get("pc_last"),
            "ps4_last": request.form.get("ps4_last"),
            "xbox_last": request.form.get("xbox_last"),
            # Reviews
            "reviews": [],
        }

        # Add player's stats to the dict
        new_player.update(get_player_stats(request.form))

        new_player_id = mongo.db.players.insert_one(new_player)

        # Send email to any interested users
        send_wishlist_email(new_player)

        return make_response(
            jsonify({"player_id": str(new_player_id.inserted_id)}), 201
        )
    else:
        return make_response(jsonify({"error": "Missing or invalid player data"}), 404)


@player.route("/api/v1.0/players/<string:player_id>", methods=["PUT"])
@jwt_required
@admin_required
def edit_player(player_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID format"}), 400)

    put_data = {}
    for key in request.form:
        put_data[key] = request.form[key]

    result = mongo.db.players.update_one(
        {"_id": ObjectId(player_id)},
        {"$set": put_data},
    )

    if result.matched_count == 1:
        return make_response(jsonify({"player_id": player_id}), 200)
    else:
        return make_response(jsonify({"error": "Invalid player ID"}), 404)


@player.route("/api/v1.0/players/<string:player_id>", methods=["DELETE"])
@jwt_required
@admin_required
def delete_player(player_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID format"}), 400)

    result = mongo.db.players.delete_one({"_id": ObjectId(player_id)})
    if result.deleted_count == 1:
        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"error": "No player found with this ID"}), 404)


def valid_post_player(player):

    """
    Due to there being such an excessive amount of data stored on each player, we only validate the presence of every field,
    and some extra validation on selected fields (mostly integer based fields)
    """

    # Validate general player details
    if (
        player.get("player_name")
        and player.get("player_extended_name")
        and player.get("overall")
        and player.get("quality")
        and player.get("revision")
        and player.get("height")
        and player.get("nationality")
        and player.get("league")
        and player.get("club")
        and player.get("position")
        and player.get("base_id")
        and player.get("pref_foot")
        and player.get("att_workrate")
        and player.get("def_workrate")
        and player.get("skill_moves")
        and player.get("weak_foot")
    ):
        if (
            1 <= int(player["overall"]) <= 99
            and player["pref_foot"] in ["Right", "Left"]
            and player["att_workrate"] in ["Low", "Medium", "High"]
            and player["def_workrate"] in ["Low", "Medium", "High"]
            and 1 <= int(player["skill_moves"]) <= 5
            and 1 <= int(player["weak_foot"]) <= 5
        ):
            # Validate player stats
            if player["position"] == "GK":
                if (
                    player.get("gk_diving")
                    and player.get("gk_reflexes")
                    and player.get("gk_handling")
                    and player.get("gk_speed")
                    and player.get("gk_kicking")
                    and player.get("gk_positioning")
                ):
                    if (
                        1 <= int(player["gk_diving"]) <= 99
                        and 1 <= int(player["gk_reflexes"]) <= 99
                        and 1 <= int(player["gk_handling"]) <= 99
                        and 1 <= int(player["gk_speed"]) <= 99
                        and 1 <= int(player["gk_kicking"]) <= 99
                        and 1 <= int(player["gk_positioning"]) <= 99
                    ):
                        return True
                    else:
                        return False
                else:
                    return False

            else:
                if (
                    player.get("pace")
                    and player.get("pace_sprint_speed")
                    and player.get("pace_acceleration")
                    and player.get("dribbling")
                    and player.get("drib_agility")
                    and player.get("drib_balance")
                    and player.get("drib_reactions")
                    and player.get("drib_ball_control")
                    and player.get("drib_dribbling")
                    and player.get("drib_composure")
                    and player.get("shooting")
                    and player.get("shoot_positioning")
                    and player.get("shoot_finishing")
                    and player.get("shoot_shot_power")
                    and player.get("shoot_long_shots")
                    and player.get("shoot_volleys")
                    and player.get("shoot_penalties")
                    and player.get("passing")
                    and player.get("pass_vision")
                    and player.get("pass_crossing")
                    and player.get("pass_free_kick")
                    and player.get("pass_short")
                    and player.get("pass_long")
                    and player.get("pass_curve")
                    and player.get("defending")
                    and player.get("def_interceptions")
                    and player.get("def_heading")
                    and player.get("def_marking")
                    and player.get("def_stand_tackle")
                    and player.get("def_slid_tackle")
                    and player.get("physicality")
                    and player.get("phys_jumping")
                    and player.get("phys_stamina")
                    and player.get("phys_strength")
                    and player.get("phys_aggression")
                ):
                    if (
                        1 <= int(player["pace"]) <= 99
                        and 1 <= int(player["pace_sprint_speed"]) <= 99
                        and 1 <= int(player["pace_acceleration"]) <= 99
                        and 1 <= int(player["dribbling"]) <= 99
                        and 1 <= int(player["drib_agility"]) <= 99
                        and 1 <= int(player["drib_balance"]) <= 99
                        and 1 <= int(player["drib_reactions"]) <= 99
                        and 1 <= int(player["drib_ball_control"]) <= 99
                        and 1 <= int(player["drib_dribbling"]) <= 99
                        and 1 <= int(player["drib_composure"]) <= 99
                        and 1 <= int(player["shooting"]) <= 99
                        and 1 <= int(player["shoot_positioning"]) <= 99
                        and 1 <= int(player["shoot_finishing"]) <= 99
                        and 1 <= int(player["shoot_shot_power"]) <= 99
                        and 1 <= int(player["shoot_long_shots"]) <= 99
                        and 1 <= int(player["shoot_volleys"]) <= 99
                        and 1 <= int(player["shoot_penalties"]) <= 99
                        and 1 <= int(player["passing"]) <= 99
                        and 1 <= int(player["pass_vision"]) <= 99
                        and 1 <= int(player["pass_crossing"]) <= 99
                        and 1 <= int(player["pass_free_kick"]) <= 99
                        and 1 <= int(player["pass_short"]) <= 99
                        and 1 <= int(player["pass_long"]) <= 99
                        and 1 <= int(player["pass_curve"]) <= 99
                        and 1 <= int(player["defending"]) <= 99
                        and 1 <= int(player["def_interceptions"]) <= 99
                        and 1 <= int(player["def_heading"]) <= 99
                        and 1 <= int(player["def_marking"]) <= 99
                        and 1 <= int(player["def_stand_tackle"]) <= 99
                        and 1 <= int(player["def_slid_tackle"]) <= 99
                        and 1 <= int(player["physicality"]) <= 99
                        and 1 <= int(player["phys_jumping"]) <= 99
                        and 1 <= int(player["phys_stamina"]) <= 99
                        and 1 <= int(player["phys_strength"]) <= 99
                        and 1 <= int(player["phys_aggression"]) <= 99
                    ):
                        return True
                    else:
                        return False
                else:
                    return False
        else:
            return False
    else:
        return False


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
        # these positions can't be modified
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


def get_players_fields(many):

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
            "league": 1,
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
    else:
        return {
            "player_name": 1,
            "player_extended_name": 1,
            "overall": 1,
            "quality": 1,
            "revision": 1,
            "origin": 1,
            "height": 1,
            "nationality": 1,
            "league": 1,
            "club": 1,
            "position": 1,
            "base_id": 1,
            "pref_foot": 1,
            "att_workrate": 1,
            "def_workrate": 1,
            "skill_moves": 1,
            "weak_foot": 1,
            "pc_last": 1,
            "ps4_last": 1,
            "xbox_last": 1,
            "reviews": 1,
            "gk_diving": 1,
            "gk_reflexes": 1,
            "gk_handling": 1,
            "gk_speed": 1,
            "gk_kicking": 1,
            "gk_positioning": 1,
            "pace": 1,
            "pace_sprint_speed": 1,
            "pace_acceleration": 1,
            "dribbling": 1,
            "drib_agility": 1,
            "drib_balance": 1,
            "drib_reactions": 1,
            "drib_ball_control": 1,
            "drib_dribbling": 1,
            "drib_composure": 1,
            "shooting": 1,
            "shoot_positioning": 1,
            "shoot_finishing": 1,
            "shoot_shot_power": 1,
            "shoot_long_shots": 1,
            "shoot_volleys": 1,
            "shoot_penalties": 1,
            "passing": 1,
            "pass_vision": 1,
            "pass_crossing": 1,
            "pass_free_kick": 1,
            "pass_short": 1,
            "pass_long": 1,
            "pass_curve": 1,
            "defending": 1,
            "def_interceptions": 1,
            "def_heading": 1,
            "def_marking": 1,
            "def_stand_tackle": 1,
            "def_slid_tackle": 1,
            "physicality": 1,
            "phys_jumping": 1,
            "phys_stamina": 1,
            "phys_strength": 1,
            "phys_aggression": 1,
        }


def get_player_stats(player):

    """
    When creating a user, we store their in game stats relative to their position (outfield or goalkeeper)
    """

    return (
        {
            "gk_diving": int(request.form.get("gk_diving")),
            "gk_reflexes": int(request.form.get("gk_reflexes")),
            "gk_handling": int(request.form.get("gk_handling")),
            "gk_speed": int(request.form.get("gk_speed")),
            "gk_kicking": int(request.form.get("gk_kicking")),
            "gk_positioning": int(request.form.get("gk_positioning")),
        }
        if player.get("position") == "GK"
        else {
            "pace": int(request.form.get("pace")),  # Pace
            "pace_sprint_speed": int(request.form.get("pace_sprint_speed")),
            "pace_acceleration": int(request.form.get("pace_acceleration")),
            "dribbling": int(request.form.get("dribbling")),  # Dribbling
            "drib_agility": int(request.form.get("drib_agility")),
            "drib_balance": int(request.form.get("drib_balance")),
            "drib_reactions": int(request.form.get("drib_reactions")),
            "drib_ball_control": int(request.form.get("drib_ball_control")),
            "drib_dribbling": int(request.form.get("drib_dribbling")),
            "drib_composure": int(request.form.get("drib_composure")),
            "shooting": int(request.form.get("shooting")),  # Shooting
            "shoot_positioning": int(request.form.get("shoot_positioning")),
            "shoot_finishing": int(request.form.get("shoot_finishing")),
            "shoot_shot_power": int(request.form.get("shoot_shot_power")),
            "shoot_long_shots": int(request.form.get("shoot_long_shots")),
            "shoot_volleys": int(request.form.get("shoot_volleys")),
            "shoot_penalties": int(request.form.get("shoot_penalties")),
            "passing": int(request.form.get("passing")),  # Passing
            "pass_vision": int(request.form.get("pass_vision")),
            "pass_crossing": int(request.form.get("pass_crossing")),
            "pass_free_kick": int(request.form.get("pass_free_kick")),
            "pass_short": int(request.form.get("pass_short")),
            "pass_long": int(request.form.get("pass_long")),
            "pass_curve": int(request.form.get("pass_curve")),
            "defending": int(request.form.get("defending")),  # Defending
            "def_interceptions": int(request.form.get("def_interceptions")),
            "def_heading": int(request.form.get("def_heading")),
            "def_marking": int(request.form.get("def_marking")),
            "def_stand_tackle": int(request.form.get("def_stand_tackle")),
            "def_slid_tackle": int(request.form.get("def_slid_tackle")),
            "physicality": int(request.form.get("physicality")),  # Physical
            "phys_jumping": int(request.form.get("phys_jumping")),
            "phys_stamina": int(request.form.get("phys_stamina")),
            "phys_strength": int(request.form.get("phys_strength")),
            "phys_aggression": int(request.form.get("phys_aggression")),
        }
    )


# players.update({}, {"$unset": {"added_date": 1, "intl_rep": 1, "weight": 1, "futbin_id": 1,}}, multi=True)


def valid_id(id):
    return True if ObjectId.is_valid(id) else False
