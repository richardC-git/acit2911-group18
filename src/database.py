import sqlite3
from pathlib import Path

from mock_data import users, studyrooms, bookings

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "roombook.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def seed_database():
    conn = get_connection()
    cursor = conn.cursor()

    for user in users:
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (id, name, email)
            VALUES (?, ?, ?)
            """,
            (user["id"], user["name"], user["email"])
        )

    for room in studyrooms:
        cursor.execute(
            """
            INSERT OR IGNORE INTO studyrooms (id, room_number, campus, description)
            VALUES (?, ?, ?, ?)
            """,
            (
                room["id"],
                room["room_number"],
                room["campus"],
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