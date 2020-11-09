from database.db import initialize_db


def register_extensions(app):
    """Adds any previously created extension objects into the app, and does any further setup they need."""

    app.config["MONGO_URI"] = "mongodb://localhost:27017/futbase"
    initialize_db(app)

    # All done!
    app.logger.info("Extensions registered")