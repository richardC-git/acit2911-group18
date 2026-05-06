# BCIT Study Room Booking System Redesign

## Overview

This project focuses on redesigning the BCIT study room booking system to improve usability, clarity, and overall user experience.

The goal is to create a simple, efficient web application that allows students to:

- View available study rooms
- Check time slot availability
- Book rooms without confusion or friction

This project is being developed using a Flask backend, SQLite database, and a lightweight HTML/CSS frontend.

## Tech Stack

- **Backend:** Python (Flask)
- **Database:** SQLite
- **Frontend:** HTML, CSS

## Features (Planned)

- View list of study rooms
- View available booking time slots
- Create a booking
- Prevent double bookings
- Display booking confirmation

## Current Status

- Initial project setup complete
- Basic workflow established
- Sprint 1 in progress

## Sprint 2 Goal
Basic CRUD functionality, finalizing page designs, implementing Peewee ORM for database, finalize database design

## Team Members

- Richard Cunningham
- Luke Dimal
- Christian Do
- Arash Farzaneh
- Joshua Otieno
- Dalli Kubat

## Run Instructions

Once cloned and synced (via `uv sync`), run this project via `uv run python src/app.py`

Visit the hosted page at http://127.0.0.1:5000

Current routes available:

- `/`
- `/my-bookings`
- `/rooms`
- `/calendar`
- `/new-booking`

_ACIT 2911 – Group 18_
