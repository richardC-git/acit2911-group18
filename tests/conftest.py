import pytest

from app import create_app
from database import (
    get_connection,
    initialize_database,
    seed_database,
)


@pytest.fixture
def app():
    app = create_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_database():
    initialize_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings")
    cursor.execute("DELETE FROM studyrooms")
    cursor.execute("DELETE FROM users")

    conn.commit()
    conn.close()

    seed_database()