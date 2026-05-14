def test_my_bookings_page_loads(client):
    # Tests that the My Bookings page loads successfully.
    # Also checks that the page has the bookings container
    # and imports the separate my-bookings.js file.
    response = client.get("/my-bookings")

    assert response.status_code == 200
    assert b"bookings-list" in response.data
    assert b"/static/js/my-bookings.js" in response.data


def test_my_bookings_js_file_loads(client):
    # Tests that the external JavaScript file for My Bookings loads correctly.
    # This helps confirm that the HTML is not relying on inline JavaScript.
    response = client.get("/static/js/my-bookings.js")

    assert response.status_code == 200


def test_api_my_bookings_returns_current_user_bookings(logged_in_client):
    # Tests that /api/my-bookings returns bookings for the logged-in user.
    response = logged_in_client.get("/api/my-bookings")
    assert response.status_code == 200

    bookings = response.get_json()
    assert isinstance(bookings, list)
    assert len(bookings) >= 1

    for booking in bookings:
        assert booking["user_id"] == 1


def test_api_my_bookings_includes_room_details(logged_in_client):
    # Tests that each booking includes room information,
    # not just raw booking IDs.
    response = logged_in_client.get("/api/my-bookings")

    assert response.status_code == 200

    bookings = response.get_json()
    first_booking = bookings[0]

    assert "room_id" in first_booking
    assert "room_number" in first_booking
    assert "campus" in first_booking
    assert "description" in first_booking
    assert "start_time" in first_booking
    assert "end_time" in first_booking
    assert "status" in first_booking


def test_api_my_bookings_excludes_other_users_bookings(logged_in_client):
    # Tests that bookings belonging to other users are not returned.
    # The mock data has bookings for users 2, 3, 4, and 5,
    # but /api/my-bookings should only return user_id 1.
    response = logged_in_client.get("/api/my-bookings")
    assert response.status_code == 200

    bookings = response.get_json()
    returned_user_ids = {booking["user_id"] for booking in bookings}
    assert returned_user_ids == {1}


def test_created_booking_appears_in_my_bookings(logged_in_client):
    # Tests that after creating a new booking,
    # it appears in the My Bookings API response.
    payload = {
        "room_id": 2,
        "start_time": "2026-05-04 09:00",
        "end_time": "2026-05-04 10:00",
    }

    create_response = logged_in_client.post("/api/bookings", json=payload)
    assert create_response.status_code == 201

    created_booking = create_response.get_json()

    my_bookings_response = logged_in_client.get("/api/my-bookings")
    assert my_bookings_response.status_code == 200

    my_bookings = my_bookings_response.get_json()

    matching_booking = next(
        (
            booking for booking in my_bookings
            if booking["id"] == created_booking["id"]
        ),
        None
    )

    assert matching_booking is not None
    assert matching_booking["user_id"] == 1
    assert matching_booking["room_id"] == 2
    assert matching_booking["start_time"] == "2026-05-04 09:00"
    assert matching_booking["end_time"] == "2026-05-04 10:00"
    assert matching_booking["status"] == "active"


def test_my_bookings_returns_empty_list_if_user_has_no_bookings(logged_in_client):
    from database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings")

    conn.commit()
    conn.close()

    response = logged_in_client.get("/api/my-bookings")

    assert response.status_code == 200
    assert response.get_json() == []