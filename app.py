from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
import jwt
import datetime
from functools import wraps
import bcrypt
import json
from views.user import user
from views.player import player
from views.wishlist import wishlist
from extensions import register_extensions

app = Flask(__name__)

# Register extensions for the app
register_extensions(app)

# Register blueprints for the app
app.register_blueprint(player)
app.register_blueprint(user)
app.register_blueprint(wishlist)

"""
In app.py, we store functionality that is used across multiple parts of the app
"""

def valid_id(id):
    if ObjectId.is_valid(id):
        return True
    else:
        return False

if __name__ == "__main__":
    app.run(debug=True)
