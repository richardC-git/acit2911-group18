import copy
import pytest

from app import create_app
from mock_data import bookings


@pytest.fixture
def app():
    app = create_app()
    app.config.update(TESTING=True)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def reset_mock_bookings():
    """
    Reset mock booking data after every test.
    """
    original_bookings = copy.deepcopy(bookings)

    yield

    bookings.clear()
    bookings.extend(original_bookings)