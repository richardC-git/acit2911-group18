from flask import Blueprint, send_from_directory, jsonify, request, session, redirect, url_for
from functools import wraps
from werkzeug.security import check_password_hash

from database import (
    get_all_rooms,
    get_room_by_id,
    get_bookings_by_user_id,
    get_booking_by_id,
    create_booking,
    update_booking,
    cancel_booking,
    has_booking_conflict,
    get_user_by_email
)

main_bp = Blueprint("main", __name__)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("user_id") is None:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("main.login_page"))
        return view(*args, **kwargs)

    return wrapped_view

AVAILABLE_SLOTS = [
    ("09:00", "10:00"),
    ("10:00", "11:00"),
    ("11:00", "12:00"),
    ("12:00", "13:00"),
    ("13:00", "14:00"),
    ("14:00", "15:00"),
    ("15:00", "16:00"),
]


@main_bp.route("/")
@login_required
def dashboard():
    return send_from_directory("static", "dashboard.html")


@main_bp.route("/rooms")
def rooms():
    return send_from_directory("static", "rooms.html")


@main_bp.route("/my-bookings")
@login_required
def my_bookings():
    return send_from_directory("static", "my-bookings.html")


@main_bp.route("/calendar")
@login_required
def calendar():
    return send_from_directory("static", "calendar.html")


@main_bp.route("/new-booking/<int:room_id>")
@login_required
def new_booking(room_id):
    return send_from_directory("static", "new-booking.html")


@main_bp.route("/api/rooms")
def api_rooms():
    rooms = get_all_rooms()
    return jsonify(rooms)


@main_bp.route("/api/rooms/<int:room_id>")
def api_room(room_id):
    room = get_room_by_id(room_id)

    if room is None:
        return jsonify({"error": "Room not found"}), 404

    return jsonify(room)


@main_bp.route("/api/rooms/<int:room_id>/available-slots")
def available_slots(room_id):
    date = request.args.get("date", "2026-05-04")
    exclude_booking_id = request.args.get("exclude_booking_id", type=int)

    room = get_room_by_id(room_id)

    if room is None:
        return jsonify({"error": "Room not found"}), 404

    available = []

    for start, end in AVAILABLE_SLOTS:
        requested_start = f"{date} {start}"
        requested_end = f"{date} {end}"

        if not has_booking_conflict(
            room_id,
            requested_start,
            requested_end,
            exclude_booking_id
        ):
            available.append({
                "start_time": requested_start,
                "end_time": requested_end,
            })

    return jsonify(available)


@main_bp.route("/api/bookings", methods=["POST"])
@login_required
def api_create_booking():
    data = request.get_json(silent=True) or {}

    room_id = data.get("room_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    user_id = session.get("user_id")

    if room_id is None or start_time is None or end_time is None:
        return jsonify({"error": "Missing booking information"}), 400

    room = get_room_by_id(room_id)

    if room is None:
        return jsonify({"error": "Room not found"}), 404

    if has_booking_conflict(room_id, start_time, end_time):
        return jsonify({"error": "Room is already booked for this time"}), 409

    new_booking = create_booking(user_id, room_id, start_time, end_time)

    return jsonify(new_booking), 201


@main_bp.route("/api/bookings/<int:booking_id>", methods=["PATCH"])
@login_required
def api_update_booking(booking_id):
    user_id = session.get("user_id")

    data = request.get_json(silent=True) or {}

    room_id = data.get("room_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if room_id is None or start_time is None or end_time is None:
        return jsonify({"error": "Missing booking information"}), 400

    room = get_room_by_id(room_id)

    if room is None:
        return jsonify({"error": "Room not found"}), 404

    booking = get_booking_by_id(booking_id)

    if booking is None:
        return jsonify({"error": "Booking not found"}), 404

    if booking["user_id"] != user_id:
        return jsonify({"error": "You cannot update another user's booking"}), 403

    if has_booking_conflict(room_id, start_time, end_time, booking_id):
        return jsonify({"error": "Room is already booked for this time"}), 409

    updated_booking = update_booking(
        booking_id,
        user_id,
        room_id,
        start_time,
        end_time
    )

    return jsonify(updated_booking), 200


@main_bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
@login_required
def api_delete_booking(booking_id):
    user_id = session.get("user_id")

    result = cancel_booking(booking_id, user_id)

    if result is None:
        return jsonify({"error": "Booking not found"}), 404

    if result == "forbidden":
        return jsonify({"error": "You cannot delete another user's booking"}), 403

    return jsonify(result), 200


@main_bp.route("/api/my-bookings")
@login_required
def api_my_bookings():
    current_user_id = session.get("user_id")

    user_bookings = get_bookings_by_user_id(current_user_id)

    return jsonify(user_bookings)

@main_bp.route("/login")
def login_page():
    return send_from_directory("static", "login.html")

# API endpoint for handling login requests
@main_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = get_user_by_email(email)

    stored_password_hash = None
    if user is not None:
        stored_password_hash = user.get("password_hash") or user.get("password")

    if user is None or not stored_password_hash or not check_password_hash(stored_password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user["id"]

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
    }), 200
    
# Logout endpoint to clear the session
@main_bp.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()

    return jsonify({"message": "Logout successful"}), 200

# Session check endpoint for frontend to determine if user is logged in
@main_bp.route("/api/session")
def api_session():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "logged_in": False,
            "user_id": None,
        }), 200

    return jsonify({
        "logged_in": True,
        "user_id": user_id,
    }), 200

