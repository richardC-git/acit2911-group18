import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

from mock_data import users, studyrooms, bookings

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "roombook.db"

DB_PATH.parent.mkdir(exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS studyrooms (
            id INTEGER PRIMARY KEY,
            room_number TEXT NOT NULL,
            campus TEXT NOT NULL,
            capacity TEXT,
            features TEXT,
            description TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def get_all_rooms():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM studyrooms
        ORDER BY id
        """
    )

    rooms = rows_to_dicts(cursor.fetchall())
    conn.close()

    return rooms


def get_room_by_id(room_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM studyrooms
        WHERE id = ?
        """,
        (room_id,)
    )

    room = cursor.fetchone()
    conn.close()

    if room is None:
        return None

    return dict(room)


def get_all_bookings():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM bookings
        ORDER BY id
        """
    )

    bookings_data = rows_to_dicts(cursor.fetchall())
    conn.close()

    return bookings_data


def get_booking_by_id(booking_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE id = ?
        """,
        (booking_id,)
    )

    booking = cursor.fetchone()
    conn.close()

    if booking is None:
        return None

    return dict(booking)


def get_active_bookings():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE status = 'active'
        ORDER BY id
        """
    )

    bookings_data = rows_to_dicts(cursor.fetchall())
    conn.close()

    return bookings_data


def get_bookings_by_user_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            bookings.id,
            bookings.user_id,
            bookings.room_id,
            bookings.start_time,
            bookings.end_time,
            bookings.status,
            studyrooms.room_number,
            studyrooms.campus,
            studyrooms.description
        FROM bookings
        JOIN studyrooms
        ON bookings.room_id = studyrooms.id
        WHERE bookings.user_id = ?
        AND bookings.status = 'active'
        ORDER BY bookings.start_time
        """,
        (user_id,)
    )

    bookings_data = rows_to_dicts(cursor.fetchall())
    conn.close()

    return bookings_data


def get_active_bookings_for_room(room_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE room_id = ?
        AND status = 'active'
        ORDER BY start_time
        """,
        (room_id,)
    )

    bookings_data = rows_to_dicts(cursor.fetchall())
    conn.close()

    return bookings_data


def has_booking_conflict(room_id, start_time, end_time, booking_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if booking_id is None:
        cursor.execute(
            """
            SELECT *
            FROM bookings
            WHERE room_id = ?
            AND status = 'active'
            AND NOT (? <= start_time OR ? >= end_time)
            """,
            (room_id, end_time, start_time)
        )
    else:
        cursor.execute(
            """
            SELECT *
            FROM bookings
            WHERE room_id = ?
            AND status = 'active'
            AND id != ?
            AND NOT (? <= start_time OR ? >= end_time)
            """,
            (room_id, booking_id, end_time, start_time)
        )

    conflict = cursor.fetchone()
    conn.close()

    return conflict is not None


def create_booking(user_id, room_id, start_time, end_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO bookings (user_id, room_id, start_time, end_time, status)
        VALUES (?, ?, ?, ?, 'active')
        """,
        (user_id, room_id, start_time, end_time)
    )

    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()

    return {
        "id": booking_id,
        "user_id": user_id,
        "room_id": room_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": "active",
    }


def update_booking(booking_id, user_id, room_id, start_time, end_time):
    booking = get_booking_by_id(booking_id)

    if booking is None:
        return None

    if booking["user_id"] != user_id:
        return "forbidden"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE bookings
        SET room_id = ?, start_time = ?, end_time = ?
        WHERE id = ?
        """,
        (room_id, start_time, end_time, booking_id)
    )

    conn.commit()
    conn.close()

    return {
        "id": booking_id,
        "user_id": user_id,
        "room_id": room_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": "active",
    }


def cancel_booking(booking_id, user_id):
    booking = get_booking_by_id(booking_id)

    if booking is None:
        return None

    if booking["user_id"] != user_id:
        return "forbidden"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE bookings
        SET status = 'cancelled'
        WHERE id = ?
        """,
        (booking_id,)
    )

    conn.commit()
    conn.close()

    booking["status"] = "cancelled"

    return booking

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email, password_hash
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return None

    return dict(user)


def seed_database():
    initialize_database()

    conn = get_connection()
    cursor = conn.cursor()

    for user in users:
        password_hash = generate_password_hash(user["password"])

        cursor.execute(
            """
            INSERT OR IGNORE INTO users (id, name, email, password_hash)
            VALUES (?, ?, ?, ?)
            """,
            (
                user["id"],
                user["name"],
                user["email"],
                password_hash
            )
        )

    for room in studyrooms:
        cursor.execute(
            """
            INSERT OR IGNORE INTO studyrooms
            (id, room_number, campus, capacity, features, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
            room["id"],
            room["room_number"],
            room["campus"],
            room["capacity"],
            room["features"],
            room["description"]
            )
        )   

    for booking in bookings:
        cursor.execute(
            """
            INSERT OR IGNORE INTO bookings
            (id, user_id, room_id, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                booking["id"],
                booking["user_id"],
                booking["room_id"],
                booking["start_time"],
                booking["end_time"],
                booking["status"]
            )
        )

    conn.commit()
    conn.close()

    print("Mock data added successfully.")


if __name__ == "__main__":
    seed_database()
