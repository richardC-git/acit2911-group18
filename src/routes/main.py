from flask import Blueprint, send_from_directory, jsonify
from mock_data import studyrooms, bookings

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def dashboard():
    return send_from_directory("static", "dashboard.html")

@main_bp.route("/rooms")
def rooms():
    return send_from_directory("static", "rooms.html")

@main_bp.route("/api/rooms")
def api_rooms():
    return jsonify(studyrooms)

AVAILABLE_SLOTS = [
    ("09:00", "10:00"),
    ("10:00", "11:00"),
    ("11:00", "12:00"),
    ("12:00", "13:00"),
    ("13:00", "14:00"),
    ("14:00", "15:00"),
    ("15:00", "16:00"),
]


@main_bp.route("/api/rooms/<int:room_id>/available-slots")
def available_slots(room_id):
    date = "2026-05-04"

    booked_slots = []

    for booking in bookings:
        if booking["room_id"] == room_id and booking["status"] == "active":
            booked_slots.append(
                (
                    booking["start_time"][11:16],
                    booking["end_time"][11:16],
                )
            )

    available = []

    for start, end in AVAILABLE_SLOTS:
        if (start, end) not in booked_slots:
            available.append(
                {
                    "start_time": f"{date} {start}",
                    "end_time": f"{date} {end}",
                }
            )

    return jsonify(available)

@main_bp.route("/my-bookings")
def my_bookings():
    return send_from_directory("static", "my-bookings.html")

@main_bp.route("/calendar")
def calendar():
    return send_from_directory("static", "calendar.html")

@main_bp.route("/new-booking")
def new_booking():
    return send_from_directory("static", "new-booking.html")