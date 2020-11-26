from flask import Blueprint, Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
import jwt
from datetime import datetime
from functools import wraps
import bcrypt
import json
from database.db import mongo
import re


review = Blueprint("review", __name__)


@review.route("/api/v1.0/players/<string:player_id>/reviews", methods=["GET"])
def get_all_reviews(player_id):

    # Get pagination details of the query
    page_num, page_size = 1, 10
    if request.args.get("pn"):
        page_num = int(request.args.get("pn"))
    if request.args.get("ps"):
        page_size = int(request.args.get("ps"))
    page_start = page_size * (page_num - 1)

    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID"}), 400)

    data_to_return = []
    # might have to change this to find instead of find_one to enable paginsation limits and sorting
    reviews = mongo.db.players.find_one({"_id": ObjectId(player_id)}, {"reviews": 1, "_id": 0})

    for review in reviews["reviews"]:
        review["_id"] = str(review["_id"])
        data_to_return.append(review)
    
    # data_to_return = sorted(data_to_return, key=lambda k: k['upvotes'], reverse=True) 

    return make_response(jsonify(data_to_return), 200)


@review.route(
    "/api/v1.0/players/<string:player_id>/reviews/<string:review_id>", methods=["GET"]
)
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

    if not request.form.get("email") or not request.form.get("comment"):
        return make_response(jsonify({"error": "Invalid review data"}), 400)

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
    "/api/v1.0/players/<string:player_id>/reviews/<string:review_id>/upvote/<string:user_id>",
    methods=["PUT"],
)
def upvote_review(player_id, review_id, user_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID format"}), 400)
    if not valid_id(review_id):
        return make_response(jsonify({"error": "Invalid review ID format"}), 400)
    if not valid_id(user_id):
        return make_response(jsonify({"error": "Invalid user ID format"}), 400)

    # only allow the user to upvote if they haven't yet done so
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
        return make_response(jsonify({"error": "This user has already upvoted this review"}), 404)

    return make_response(jsonify({"review_id": review_id}), 200)

@review.route(
    "/api/v1.0/players/<string:player_id>/reviews/<string:review_id>/downvote/<string:user_id>",
    methods=["PUT"],
)
def downvote_review(player_id, review_id, user_id):
    if not valid_id(player_id):
        return make_response(jsonify({"error": "Invalid player ID format"}), 400)
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
        return make_response(jsonify({"error": "This user has already downvoted this review"}), 404)

    return make_response(jsonify({"review_id": review_id}), 200)


def valid_id(id):
    return True if ObjectId.is_valid(id) else False

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
