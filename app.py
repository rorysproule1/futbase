from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
import jwt
import datetime
from functools import wraps
import bcrypt

app = Flask(__name__)
client = MongoClient("mongodb://127.0.0.1:27017")

db = client.futbin
players = db.players

app.config["SECRET_KEY"] = "mysecret"

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/api/v1.0/players", methods=["GET"])
def show_all_players():
    page_num, page_size = 1, 10
    if request.args.get("pn"):
        page_num = int(request.args.get("pn"))
    if request.args.get("ps"):
        page_size = int(request.args.get("ps"))
    page_start = page_size * (page_num - 1)

    data_to_return = []
    for player in players.find().skip(page_start).limit(page_size):
        data_to_return.append(player["player_name"])
    return make_response(jsonify(data_to_return), 200)
