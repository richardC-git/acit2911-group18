from flask import Blueprint, send_from_directory

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def dashboard():
    return send_from_directory("static", "dashboard.html")

@main_bp.route("/rooms")
def rooms():
    return send_from_directory("static", "rooms.html")

@main_bp.route("/my-bookings")
def my_bookings():
    return send_from_directory("static", "my-bookings.html")

@main_bp.route("/calendar")
def calendar():
    return send_from_directory("static", "calendar.html")

@main_bp.route("/new-booking")
def new_booking():
    return send_from_directory("static", "new-booking.html")