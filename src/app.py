import os

from flask import Flask, request, session, redirect, url_for
from routes.main import main_bp


def create_app():
    app = Flask(__name__, static_folder="static")

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "team-18-should-use-a-secure-secret-key-in-production",
    )

    app.register_blueprint(main_bp)

    PROTECTED_STATIC_HTML = {
        "/static/dashboard.html",
        "/static/my-bookings.html",
        "/static/new-booking.html",
        "/static/calendar.html",
    }

    @app.before_request
    def require_login_for_protected_static_pages():
        if request.path in PROTECTED_STATIC_HTML and session.get("user_id") is None:
            return redirect(url_for("main.login_page"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)