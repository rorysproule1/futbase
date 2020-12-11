from flask import Blueprint, request, jsonify, make_response
from bson import ObjectId
from datetime import datetime
from functools import wraps
from database.db import mongo
from views.authenticate import jwt_required
from operator import itemgetter
import re


review = Blueprint("review", __name__)


@review.route("/api/v1.0/players/<string:player_id>/reviews", methods=["GET"])
@jwt_required
def get_all_reviews(player_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID"}), 400)

    # Get pagination details of the query
    page_num, page_size = 1, 5
    if request.args.get("pn"):
        page_num = int(request.args.get("pn"))
    if request.args.get("ps"):
        page_size = int(request.args.get("ps"))
    page_start = page_size * (page_num - 1)

    reviews = mongo.db.players.find_one(
        {"_id": ObjectId(player_id)}, {"reviews": 1, "_id": 0}
    )
    player_reviews = reviews["reviews"]

    # Sort based on sort parameter (recent, popular, unpopular)
    player_reviews = sort_reviews(player_reviews, request.args.get("sort"))

    data_to_return = [{"review_count": len(player_reviews)}]
    for review in player_reviews[page_start : page_start + page_size]:
        review["_id"] = str(review["_id"])
        data_to_return.append(review)

    return make_response(jsonify(data_to_return), 200)


@review.route(
    "/api/v1.0/players/<string:player_id>/reviews/<string:review_id>", methods=["GET"]
)
@jwt_required
def get_one_review(player_id, review_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID format"}), 400)
    if not valid_id(review_id):
        return make_response(jsonify({"error": "Invalid review ID format"}), 400)

    reviews = mongo.db.players.find_one(
        {"reviews._id": ObjectId(review_id)}, {"_id": 0, "reviews.$": 1}
    )
    if reviews is None:
        return make_response(
            jsonify(
                {
                    "error": "Could not find a review with the player and review IDs provided"
                }
            ),
            404,
        )
    reviews["reviews"][0]["_id"] = str(reviews["reviews"][0]["_id"])

    return make_response(jsonify(reviews["reviews"][0]), 200)


@review.route("/api/v1.0/players/<string:player_id>/reviews", methods=["POST"])
def add_review(player_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID format"}), 400)
    if not valid_review(request.form):
        return make_response(jsonify({"error": "Invalid review data"}), 400)

    print(request.form)

    new_review = {
        "_id": ObjectId(),
        "user": request.form["email"],
        "comment": request.form["comment"],
        "date": datetime.now(),
        "upvotes": 0,
        "upvoters": [],
        "downvoters": [],
    }
    mongo.db.players.update_one(
        {"_id": ObjectId(player_id)}, {"$push": {"reviews": new_review}}
    )

    return make_response(jsonify({"review_id": str(new_review["_id"])}), 201)


@review.route(
    "/api/v1.0/players/<string:player_id>/reviews/<string:review_id>",
    methods=["DELETE"],
)
@jwt_required
def delete_review(player_id, review_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID format"}), 400)
    if not valid_id(review_id):
        return make_response(jsonify({"error": "Invalid review ID format"}), 400)

    mongo.db.players.update_one(
        {"_id": ObjectId(player_id)},
        {"$pull": {"reviews": {"_id": ObjectId(review_id)}}},
    )
    return make_response(jsonify({}), 204)


@review.route(
    "/api/v1.0/reviews/<string:review_id>/upvote/<string:user_id>",
    methods=["PUT"],
)
@jwt_required
def upvote_review(review_id, user_id):
    if not valid_id(review_id):
        return make_response(jsonify({"error": "Invalid review ID format"}), 400)
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID format"}), 400)

    # Only allow the user to upvote if they haven't yet done so
    if user_id not in get_upvoters(review_id):
        mongo.db.players.update_one(
            {"reviews._id": ObjectId(review_id)},
            {
                "$addToSet": {"reviews.$.upvoters": user_id},
                "$inc": {"reviews.$.upvotes": 1},
                "$pull": {"reviews.$.downvoters": user_id},
            },
        )
    else:
        return make_response(
            jsonify({"error": "This user has already upvoted this review"}), 404
        )

    return make_response(jsonify({"review_id": review_id}), 200)


@review.route(
    "/api/v1.0/reviews/<string:review_id>/downvote/<string:user_id>",
    methods=["PUT"],
)
@jwt_required
def downvote_review(review_id, user_id):
    if not valid_id(review_id):
        return make_response(jsonify({"error": "Invalid review ID format"}), 400)
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID format"}), 400)

    # Only allow the user to downvote if they haven't yet done so
    if user_id not in get_downvoters(review_id):
        mongo.db.players.update_one(
            {"reviews._id": ObjectId(review_id)},
            {
                "$pull": {"reviews.$.upvoters": user_id},
                "$inc": {"reviews.$.upvotes": -1},
                "$addToSet": {"reviews.$.downvoters": user_id},
            },
        )
    else:
        return make_response(
            jsonify({"error": "This user has already downvoted this review"}), 404
        )

    return make_response(jsonify({"review_id": review_id}), 200)


def sort_reviews(reviews, sort_parameter):
    sort_type = (
        "recent"
        if sort_parameter == "recent"
        else "popular"
        if sort_parameter == "popular"
        else "unpopular"
        if sort_parameter == "unpopular"
        else "recent"
    )
    if sort_type == "popular":
        reviews = sorted(reviews, key=itemgetter("upvotes"), reverse=True)
    if sort_type == "unpopular":
        reviews = sorted(reviews, key=itemgetter("upvotes"), reverse=False)
    if sort_type == "recent":
        reviews = sorted(reviews, key=itemgetter("date"), reverse=True)
    
    return reviews


def valid_id(id):
    return True if ObjectId.is_valid(id) else False


def valid_review(review):
    if review.get("email") and review.get("comment"):
        if len(review["comment"]) < 1000 and mongo.db.users.find_one(
            {"email": review["email"]}
        ):
            return True
    return False


def get_downvoters(review_id):
    review = mongo.db.players.find_one(
        {"reviews._id": ObjectId(review_id)}, {"_id": 0, "reviews.$": 1}
    )

    return review["reviews"][0]["downvoters"]


def get_upvoters(review_id):
    review = mongo.db.players.find_one(
        {"reviews._id": ObjectId(review_id)}, {"_id": 0, "reviews.$": 1}
    )

    return review["reviews"][0]["upvoters"]
