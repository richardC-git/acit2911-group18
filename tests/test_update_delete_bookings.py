def test_update_booking_successfully(client):
    # Tests that an existing booking can be updated to a new available time slot.
    # This first creates a booking, then updates it using PATCH.

    create_payload = {
        "room_id": 1,
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    create_response = client.post("/api/bookings", json=create_payload)
    assert create_response.status_code == 201

    created_booking = create_response.get_json()
    booking_id = created_booking["id"]

    update_payload = {
        "room_id": 1,
        "start_time": "2026-05-04 10:00",
        "end_time": "2026-05-04 11:00",
    }

    update_response = client.patch(f"/api/bookings/{booking_id}", json=update_payload)
    assert update_response.status_code == 200

    updated_booking = update_response.get_json()
    assert updated_booking["id"] == booking_id
    assert updated_booking["room_id"] == 1
    assert updated_booking["start_time"] == "2026-05-04 10:00"
    assert updated_booking["end_time"] == "2026-05-04 11:00"
    assert updated_booking["status"] == "active"


def test_update_booking_frees_old_time_slot(client):
    # Tests that when a booking is updated,
    # the old time slot becomes available again.

    create_payload = {
        "room_id": 1,
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    create_response = client.post("/api/bookings", json=create_payload)
    assert create_response.status_code == 201

    booking_id = create_response.get_json()["id"]

    update_payload = {
        "room_id": 1,
        "start_time": "2026-05-04 10:00",
        "end_time": "2026-05-04 11:00",
    }

    update_response = client.patch(f"/api/bookings/{booking_id}", json=update_payload)
    assert update_response.status_code == 200

    slots_response = client.get("/api/rooms/1/available-slots?date=2026-05-04")
    assert slots_response.status_code == 200

    slots = slots_response.get_json()

    old_slot = {
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    new_slot = {
        "start_time": "2026-05-04 10:00",
        "end_time": "2026-05-04 11:00",
    }

    assert old_slot in slots
    assert new_slot not in slots


def test_update_booking_rejects_conflicting_time_slot(client):
    # Tests that a booking cannot be updated to a time slot
    # that is already booked by another active booking.
    #
    # Room 1 already has 11:00-12:00 booked in the mock data.

    create_payload = {
        "room_id": 1,
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    create_response = client.post("/api/bookings", json=create_payload)
    assert create_response.status_code == 201

    booking_id = create_response.get_json()["id"]

    update_payload = {
        "room_id": 1,
        "start_time": "2026-05-04 11:00",
        "end_time": "2026-05-04 12:00",
    }

    update_response = client.patch(f"/api/bookings/{booking_id}", json=update_payload)
    assert update_response.status_code == 409

    data = update_response.get_json()
    assert data["error"] == "Room is already booked for this time"


def test_update_booking_rejects_missing_data(client):
    # Tests that updating a booking fails if required fields are missing.

    update_payload = {
        "room_id": 1,
        "start_time": "2026-05-04 09:00",
    }

    response = client.patch("/api/bookings/1", json=update_payload)
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Missing booking information"


def test_update_booking_rejects_invalid_room(client):
    # Tests that updating a booking fails if the new room ID does not exist.

    update_payload = {
        "room_id": 999,
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    response = client.patch("/api/bookings/1", json=update_payload)
    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Room not found"


def test_update_booking_rejects_booking_not_found(client):
    # Tests that updating a booking fails if the booking ID does not exist.

    update_payload = {
        "room_id": 1,
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    response = client.patch("/api/bookings/999", json=update_payload)
    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Booking not found"


def test_update_booking_rejects_other_users_booking(client):
    # Tests that the current user cannot update another user's booking.
    #
    # Until login exists, current user is assumed to be user_id 1.
    # Booking ID 2 belongs to user_id 2 in the mock data.

    update_payload = {
        "room_id": 4,
        "start_time": "2026-05-04 10:00",
        "end_time": "2026-05-04 11:00",
    }

    response = client.patch("/api/bookings/2", json=update_payload)
    assert response.status_code == 403

    data = response.get_json()
    assert data["error"] == "You cannot update another user's booking"


def test_delete_booking_marks_booking_as_cancelled(client):
    # Tests that deleting a booking marks it as cancelled.
    # This is a soft delete, not a permanent delete.

    response = client.delete("/api/bookings/1")
    assert response.status_code == 200

    booking = response.get_json()
    assert booking["id"] == 1
    assert booking["status"] == "cancelled"


def test_deleted_booking_time_slot_becomes_available(client):
    # Tests that after a booking is deleted/cancelled,
    # its time slot becomes available again.
    #
    # Room 1 has 11:00-12:00 booked in the mock data.

    delete_response = client.delete("/api/bookings/1")
    assert delete_response.status_code == 200

    slots_response = client.get("/api/rooms/1/available-slots?date=2026-05-04")
    assert slots_response.status_code == 200

    slots = slots_response.get_json()
    cancelled_slot = {
        "start_time": "2026-05-04 11:00",
        "end_time": "2026-05-04 12:00",
    }

    assert cancelled_slot in slots


def test_delete_booking_rejects_booking_not_found(client):
    # Tests that deleting a booking fails if the booking ID does not exist.

    response = client.delete("/api/bookings/999")
    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Booking not found"


def test_delete_booking_rejects_other_users_booking(client):
    # Tests that the current user cannot delete another user's booking.
    #
    # Until login exists, current user is assumed to be user_id 1.
    # Booking ID 2 belongs to user_id 2 in the mock data.

    response = client.delete("/api/bookings/2")
    assert response.status_code == 403

    data = response.get_json()
    assert data["error"] == "You cannot delete another user's booking"