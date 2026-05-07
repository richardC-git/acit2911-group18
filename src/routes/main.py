from flask import Blueprint, send_from_directory, jsonify, request
from mock_data import studyrooms, bookings

main_bp = Blueprint("main", __name__)

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


@main_bp.route("/new-booking/<int:room_id>")
def new_booking(room_id):
    return send_from_directory("static", "new-booking.html")


@main_bp.route("/api/rooms")
def api_rooms():
    return jsonify(studyrooms)


@main_bp.route("/api/rooms/<int:room_id>")
def api_room(room_id):
    room = next((room for room in studyrooms if room["id"] == room_id), None)

    if room is None:
        return jsonify({"error": "Room not found"}), 404

    return jsonify(room)


@main_bp.route("/api/rooms/<int:room_id>/available-slots")
def available_slots(room_id):
    date = request.args.get("date", "2026-05-04")

    room = next((room for room in studyrooms if room["id"] == room_id), None)

    if room is None:
        return jsonify({"error": "Room not found"}), 404

    available = []

    for start, end in AVAILABLE_SLOTS:
        requested_start = f"{date} {start}"
        requested_end = f"{date} {end}"

        conflict = False

        for booking in bookings:
            if booking["room_id"] != room_id:
                continue

            if booking["status"] != "active":
                continue

            overlaps = not (
                requested_end <= booking["start_time"]
                or requested_start >= booking["end_time"]
            )

            if overlaps:
                conflict = True
                break

        if not conflict:
            available.append({
                "start_time": requested_start,
                "end_time": requested_end,
            })

    return jsonify(available)


@main_bp.route("/api/bookings", methods=["POST"])
def create_booking():
    
    data = request.get_json()

    room_id = data.get("room_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    # Temporary until login exists
    user_id = 1

    if room_id is None or start_time is None or end_time is None:
        return jsonify({"error": "Missing booking information"}), 400

    room = next((room for room in studyrooms if room["id"] == room_id), None)

    if room is None:
        return jsonify({"error": "Room not found"}), 404

    for booking in bookings:
        if booking["room_id"] != room_id:
            continue

        if booking["status"] != "active":
            continue

        overlaps = not (
            end_time <= booking["start_time"]
            or start_time >= booking["end_time"]
        )

        if overlaps:
            return jsonify({"error": "Room is already booked for this time"}), 409

    new_booking = {
        "id": len(bookings) + 1,
        "user_id": user_id,
        "room_id": room_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": "active",
    }

    bookings.append(new_booking)

    return jsonify(new_booking), 201

@main_bp.route("/api/my-bookings")
def api_my_bookings():
    # Temporary until login exists
    current_user_id = 1

    user_bookings = []

    for booking in bookings:
        if booking["user_id"] != current_user_id:
            continue

        room = next(
            (room for room in studyrooms if room["id"] == booking["room_id"]),
            None
        )

        user_bookings.append({
            "id": booking["id"],
            "user_id": booking["user_id"],
            "room_id": booking["room_id"],
            "room_number": room["room_number"] if room else "Unknown",
            "campus": room["campus"] if room else "Unknown",
            "description": room["description"] if room else "",
            "start_time": booking["start_time"],
            "end_time": booking["end_time"],
            "status": booking["status"],
        })

    return jsonify(user_bookings)