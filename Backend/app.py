from flask import Flask
from views.authenticate import authenticate
from views.user import user
from views.player import player
from views.wishlist import wishlist
from views.review import review
from extensions import register_extensions
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register extensions for the app
register_extensions(app)

# Register blueprints for the app
app.register_blueprint(authenticate)
app.register_blueprint(player)
app.register_blueprint(user)
app.register_blueprint(wishlist)
app.register_blueprint(review)


if __name__ == "__main__":
    app.run(debug=True)
