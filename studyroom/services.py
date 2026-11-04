"""Business rules. No Flask, no SQL: easy to test and to read.

Demo 2 (week 13, slide 28): change MAX_HOURS from 3 to 4, push a branch,
open a PR and watch `test_booking_3h30_is_rejected` turn CI red.
"""
from datetime import datetime, time, timedelta

from . import repository

MAX_HOURS = 3                      # a booking lasts at most 3 hours
OPENING_TIME = time(7, 0)          # the room opens at 07:00
CLOSING_TIME = time(22, 0)         # and closes at 22:00
CHECKIN_WINDOW = timedelta(minutes=15)


class BookingError(Exception):
    """A rule was broken. `status` is the HTTP code the API returns."""

    def __init__(self, status, code, message):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def parse_time(value, field):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise BookingError(
            422, "INVALID_TIME", f"'{field}' must look like 2026-11-20T09:00."
        )


def create_booking(student_id, desk_id, start, end, now=None):
    now = now or datetime.now()
    if not student_id:
        raise BookingError(422, "MISSING_STUDENT", "Please enter your student ID.")
    if not isinstance(desk_id, int):
        raise BookingError(422, "MISSING_DESK", "Please choose a desk.")
    if not repository.desk_exists(desk_id):
        raise BookingError(404, "DESK_NOT_FOUND", "This desk does not exist.")
    if end <= start:
        raise BookingError(422, "END_BEFORE_START", "The end time must be after the start time.")
    if start < now:
        raise BookingError(422, "START_IN_PAST", "You cannot book a time in the past.")
    if end - start > timedelta(hours=MAX_HOURS):
        raise BookingError(
            422, "TOO_LONG", f"A booking can last at most {MAX_HOURS} hours."
        )
    if (
        start.date() != end.date()
        or start.time() < OPENING_TIME
        or end.time() > CLOSING_TIME
    ):
        raise BookingError(
            422, "OUTSIDE_OPENING_HOURS", "The study room is open from 07:00 to 22:00."
        )
    if repository.find_active_booking(student_id, now.isoformat()):
        raise BookingError(
            409, "ALREADY_HAS_BOOKING", "You already have an active booking. Cancel it first."
        )
    if repository.desk_is_taken(desk_id, start.isoformat(), end.isoformat()):
        raise BookingError(409, "DESK_TAKEN", "This desk is already booked at that time.")
    return repository.insert_booking(student_id, desk_id, start.isoformat(), end.isoformat())


def check_in(booking_id, now=None):
    now = now or datetime.now()
    booking = repository.get_booking(booking_id)
    if booking is None:
        raise BookingError(404, "BOOKING_NOT_FOUND", "This booking does not exist.")
    if booking["status"] != "booked":
        raise BookingError(409, "NOT_BOOKED", "This booking is already checked in or cancelled.")
    start = datetime.fromisoformat(booking["start_time"])
    if not (start - CHECKIN_WINDOW <= now <= start + CHECKIN_WINDOW):
        raise BookingError(
            422, "CHECKIN_WINDOW", "Check-in is open from 15 minutes before to 15 minutes after the start."
        )
    return repository.set_status(booking_id, "checked_in")
