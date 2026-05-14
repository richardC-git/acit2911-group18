def test_session_reports_logged_out_when_no_user_is_logged_in(client):
    # Tests that the session endpoint reports the user as logged out
    # before any login has happened.
    response = client.get("/api/session")

    assert response.status_code == 200

    data = response.get_json()

    assert data["logged_in"] is False
    assert data["user_id"] is None


def test_login_succeeds_with_valid_credentials(client):
    # Tests that a user can log in with a valid email and password.
    # It also checks that basic user information is returned.
    payload = {
        "email": "richard@example.com",
        "password": "studyroom123",
    }

    response = client.post("/api/login", json=payload)

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Login successful"
    assert data["user"]["id"] == 1
    assert data["user"]["name"] == "Richard Cunningham"
    assert data["user"]["email"] == "richard@example.com"


def test_login_stores_user_id_in_session(client):
    # Tests that a successful login stores the user's ID
    # in the Flask session.
    payload = {
        "email": "richard@example.com",
        "password": "studyroom123",
    }

    response = client.post("/api/login", json=payload)

    assert response.status_code == 200

    with client.session_transaction() as session_data:
        assert session_data["user_id"] == 1


def test_session_reports_logged_in_after_successful_login(client):
    # Tests that after logging in,
    # the session endpoint reports the user as logged in.
    payload = {
        "email": "richard@example.com",
        "password": "studyroom123",
    }

    login_response = client.post("/api/login", json=payload)

    assert login_response.status_code == 200

    session_response = client.get("/api/session")

    assert session_response.status_code == 200

    data = session_response.get_json()

    assert data["logged_in"] is True
    assert data["user_id"] == 1


def test_login_rejects_invalid_email(client):
    # Tests that login fails when the submitted email
    # does not exist in the database.
    payload = {
        "email": "notreal@example.com",
        "password": "studyroom123",
    }

    response = client.post("/api/login", json=payload)

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Invalid email or password"


def test_login_rejects_invalid_password(client):
    # Tests that login fails when the password is incorrect.
    payload = {
        "email": "richard@example.com",
        "password": "wrongpassword",
    }

    response = client.post("/api/login", json=payload)

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Invalid email or password"


def test_login_rejects_missing_email(client):
    # Tests that login fails when no email is provided.
    payload = {
        "password": "studyroom123",
    }

    response = client.post("/api/login", json=payload)

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Email and password are required"


def test_login_rejects_missing_password(client):
    # Tests that login fails when no password is provided.
    payload = {
        "email": "richard@example.com",
    }

    response = client.post("/api/login", json=payload)

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Email and password are required"


def test_login_rejects_empty_json_body(client):
    # Tests that login fails safely when the request body
    # contains no email or password at all.
    response = client.post("/api/login", json={})

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Email and password are required"


def test_logout_clears_session(client):
    # Tests that logging out removes the user ID
    # from the Flask session.
    login_payload = {
        "email": "richard@example.com",
        "password": "studyroom123",
    }

    login_response = client.post("/api/login", json=login_payload)

    assert login_response.status_code == 200

    logout_response = client.post("/api/logout")

    assert logout_response.status_code == 200

    data = logout_response.get_json()

    assert data["message"] == "Logout successful"

    with client.session_transaction() as session_data:
        assert "user_id" not in session_data


def test_session_reports_logged_out_after_logout(client):
    # Tests that the session endpoint reports the user as logged out
    # after the logout route has been called.
    login_payload = {
        "email": "richard@example.com",
        "password": "studyroom123",
    }

    login_response = client.post("/api/login", json=login_payload)

    assert login_response.status_code == 200

    logout_response = client.post("/api/logout")

    assert logout_response.status_code == 200

    session_response = client.get("/api/session")

    assert session_response.status_code == 200

    data = session_response.get_json()

    assert data["logged_in"] is False
    assert data["user_id"] is None