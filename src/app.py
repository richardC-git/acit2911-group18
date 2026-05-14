import os

from flask import Flask
from routes.main import main_bp


def create_app():
    app = Flask(__name__, static_folder="static")

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "team-18-should-use-a-secure-secret-key-in-production",
    )

    app.register_blueprint(main_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)