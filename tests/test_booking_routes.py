def test_rooms_page_loads(client):
    # Tests that the Rooms page loads successfully.
    # Also checks that the page contains the rooms list container
    # and imports the separate rooms.js file.
    response = client.get("/rooms")

    assert response.status_code == 200
    assert b"rooms-list" in response.data
    assert b"/static/js/rooms.js" in response.data


def test_new_booking_page_loads_for_room_id(client):
    # Tests that the New Booking page loads when given a room ID.
    # Also checks that the page imports the separate new-booking.js file.
    response = client.get("/new-booking/1")

    assert response.status_code == 200
    assert b"New Booking" in response.data
    assert b"/static/js/new-booking.js" in response.data


def test_api_get_single_room(client):
    # Tests that the API can return one room by its room ID.
    # This confirms that /api/rooms/1 returns the expected room data.
    response = client.get("/api/rooms/1")
    assert response.status_code == 200

    room = response.get_json()
    assert room["id"] == 1
    assert room["room_number"] == "582"
    assert "campus" in room
    assert "description" in room


def test_api_get_invalid_room_returns_404(client):
    # Tests that the API returns a 404 error when the room ID does not exist.
    response = client.get("/api/rooms/999")
    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Room not found"


def test_available_slots_excludes_already_booked_time(client):
    # Tests that available slots do not include times that are already booked.
    # Room 1 already has 11:00-12:00 booked in the mock data.
    response = client.get("/api/rooms/1/available-slots?date=2026-05-04")
    assert response.status_code == 200

    slots = response.get_json()
    
    booked_slot = {
        "start_time": "2026-05-04 11:00",
        "end_time": "2026-05-04 12:00",
    }
    
    available_slot = {
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    assert booked_slot not in slots
    assert available_slot in slots


def test_create_booking_successfully(client):
    # Tests that a user can create a booking for an available time slot.
    # This should return the new booking with a 201 Created response.
    payload = {
        "room_id": 1,
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    response = client.post("/api/bookings", json=payload)
    assert response.status_code == 201

    booking = response.get_json()
    assert booking["room_id"] == 1
    assert booking["user_id"] == 1
    assert booking["start_time"] == "2026-05-04 09:00"
    assert booking["end_time"] == "2026-05-04 10:00"
    assert booking["status"] == "active"


def test_created_booking_is_removed_from_available_slots(client):
    # Tests that after a booking is created,
    # that same time slot no longer appears as available.
    payload = {
        "room_id": 1,
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    create_response = client.post("/api/bookings", json=payload)
    assert create_response.status_code == 201

    slots_response = client.get("/api/rooms/1/available-slots?date=2026-05-04")
    assert slots_response.status_code == 200

    slots = slots_response.get_json()
    assert payload not in slots


def test_create_booking_rejects_conflicting_booking(client):
    # Tests that the API rejects a booking if the room is already booked
    # during the requested time.
    payload = {
        "room_id": 1,
        "start_time": "2026-05-04 11:00",
        "end_time": "2026-05-04 12:00",
    }

    response = client.post("/api/bookings", json=payload)
    assert response.status_code == 409

    data = response.get_json()
    assert data["error"] == "Room is already booked for this time"


def test_create_booking_rejects_missing_data(client):
    # Tests that the API rejects a booking request
    # if required information is missing.
    payload = {
        "room_id": 1,
        "start_time": "2026-05-04 09:00",
    }

    response = client.post("/api/bookings", json=payload)
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Missing booking information"


def test_create_booking_rejects_invalid_room(client):
    # Tests that the API rejects a booking request
    # if the room ID does not exist.
    payload = {
        "room_id": 999,
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    response = client.post("/api/bookings", json=payload)
    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Room not found"