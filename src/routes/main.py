from flask import Blueprint, send_from_directory

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return send_from_directory("static", "index.html")

@main_bp.route("/rooms")
def rooms():
    return send_from_directory("static", "rooms.html")

@main_bp.route("/bookings")
def bookings():
    return send_from_directory("static", "bookings.html")

@main_bp.route("/sample")
def sample():
    return send_from_directory("static", "project.html")