#!/usr/bin/env python3
"""api_server.py — Elite Traders Lounge backend.

Handles babysitter registration, parent/guardian registration + booking
requests, and the dual (babysitter + parent/guardian) arrival/departure
confirmation system used to track worked hours for every booking.

Runs on port 8000 inside the sandbox.
"""
import random
import re
import sqlite3
import string
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(v: str) -> str:
    if not EMAIL_RE.match(v.strip()):
        raise ValueError("invalid email address")
    return v.strip()

DB_PATH = "data.db"


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


db = get_db()
db.executescript(
    """
    CREATE TABLE IF NOT EXISTS babysitters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        id_number TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        experience_level TEXT NOT NULL,
        years_experience TEXT NOT NULL,
        certifications TEXT,
        references_text TEXT NOT NULL,
        availability TEXT NOT NULL,
        bank_name TEXT NOT NULL,
        account_holder TEXT NOT NULL,
        account_number TEXT NOT NULL,
        agreed_terms INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'pending_verification',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_ref TEXT UNIQUE NOT NULL,
        pin TEXT NOT NULL,
        parent_name TEXT NOT NULL,
        id_number TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        children_count TEXT NOT NULL,
        booking_date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        rate_type TEXT NOT NULL,
        level TEXT NOT NULL,
        hourly_rate REAL NOT NULL,
        duration_hours REAL NOT NULL,
        special_instructions TEXT,
        status TEXT NOT NULL DEFAULT 'pending_match',
        agreed_terms INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_ref TEXT NOT NULL,
        role TEXT NOT NULL,
        action TEXT NOT NULL,
        note TEXT,
        timestamp TEXT NOT NULL
    );
    """
)
db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

LEVELS = {"1", "2", "3", "4"}
RATE_TYPES = {"day", "overnight"}
ROLES = {"sitter", "parent"}
ACTIONS = {"arrival", "departure"}

# Appendix C — rate bands (hourly, ZAR) and commission rules, aligned to the
# 2026/2027 National Minimum Wage of R30.23/hour (effective 1 March 2026,
# Government Gazette No. 54075).
NATIONAL_MINIMUM_WAGE = 30.23

RATE_BANDS = {
    ("1", "day"): {"min": 35, "max": 45, "commission": lambda r: 0.10},
    ("2", "day"): {"min": 45, "max": 65, "commission": lambda r: 0.125},
    ("3", "day"): {"min": 65, "max": 85, "commission": lambda r: 0.125 + 0.025 * max(0, min(1, (r - 65) / 20))},
    ("3", "overnight"): {"min": 70, "max": 80, "commission": lambda r: 0.125},
    ("4", "overnight"): {"min": 90, "max": 100, "commission": lambda r: 0.125},
}
MIN_HOURS = {"day": 4, "overnight": 10}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def gen_booking_ref() -> str:
    for _ in range(20):
        ref = "ETL-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not db.execute("SELECT 1 FROM bookings WHERE booking_ref = ?", (ref,)).fetchone():
            return ref
    raise RuntimeError("could not generate a unique booking reference")


def gen_pin() -> str:
    return "".join(random.choices(string.digits, k=4))


class SitterRegistration(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    id_number: str = Field(min_length=5, max_length=20)
    phone: str = Field(min_length=7, max_length=20)
    email: str
    address: str = Field(min_length=5, max_length=300)
    experience_level: str
    years_experience: str
    certifications: Optional[str] = ""
    references_text: str = Field(min_length=5, max_length=1000)
    availability: str = Field(min_length=2, max_length=300)
    bank_name: str = Field(min_length=2, max_length=100)
    account_holder: str = Field(min_length=2, max_length=120)
    account_number: str = Field(min_length=4, max_length=40)
    agreed_terms: bool

    _validate_email = field_validator("email")(validate_email)

    @field_validator("experience_level")
    @classmethod
    def check_level(cls, v):
        if v not in LEVELS:
            raise ValueError("experience_level must be 1, 2, 3 or 4")
        return v

    @field_validator("agreed_terms")
    @classmethod
    def check_agreed(cls, v):
        if not v:
            raise ValueError("you must accept the babysitter contract terms to register")
        return v


class BookingRequest(BaseModel):
    parent_name: str = Field(min_length=2, max_length=120)
    id_number: str = Field(min_length=5, max_length=20)
    phone: str = Field(min_length=7, max_length=20)
    email: str
    address: str = Field(min_length=5, max_length=300)
    children_count: str = Field(min_length=1, max_length=20)

    _validate_email = field_validator("email")(validate_email)
    booking_date: str
    start_time: str
    rate_type: str
    level: str
    hourly_rate: float = Field(gt=0)
    duration_hours: float = Field(gt=0)
    special_instructions: Optional[str] = ""
    agreed_terms: bool

    @field_validator("level")
    @classmethod
    def check_level(cls, v):
        if v not in LEVELS:
            raise ValueError("level must be 1, 2, 3 or 4")
        return v

    @field_validator("rate_type")
    @classmethod
    def check_rate_type(cls, v):
        if v not in RATE_TYPES:
            raise ValueError("rate_type must be 'day' or 'overnight'")
        return v

    @field_validator("agreed_terms")
    @classmethod
    def check_agreed(cls, v):
        if not v:
            raise ValueError("you must accept the booking contract terms to submit a booking")
        return v


class CheckinRequest(BaseModel):
    booking_ref: str
    pin: str
    role: str
    action: str
    note: Optional[str] = ""

    @field_validator("role")
    @classmethod
    def check_role(cls, v):
        if v not in ROLES:
            raise ValueError("role must be 'sitter' or 'parent'")
        return v

    @field_validator("action")
    @classmethod
    def check_action(cls, v):
        if v not in ACTIONS:
            raise ValueError("action must be 'arrival' or 'departure'")
        return v


def compute_rate_check(level: str, rate_type: str, hourly_rate: float, duration_hours: float):
    band = RATE_BANDS.get((level, rate_type))
    if band is None:
        raise HTTPException(422, f"Level {level} has no {rate_type} rate band. Level 1 and 2 are day-only; Level 3 supports day and overnight; Level 4 is overnight/specialist only.")
    min_hours = MIN_HOURS[rate_type]
    if duration_hours < min_hours:
        raise HTTPException(422, f"Minimum booking length for a {rate_type} booking is {min_hours} hours.")
    applied_rate = hourly_rate
    compliance_note = "within band"
    if hourly_rate < NATIONAL_MINIMUM_WAGE or hourly_rate < band["min"]:
        applied_rate = max(band["min"], NATIONAL_MINIMUM_WAGE)
        compliance_note = f"rate below the Level {level} {rate_type} minimum (R{band['min']}/hour) or below the National Minimum Wage (R{NATIONAL_MINIMUM_WAGE}/hour) — automatically corrected to R{applied_rate}/hour per Appendix C"
    elif hourly_rate > band["max"]:
        compliance_note = f"rate is above the Level {level} {rate_type} band ceiling (R{band['max']}/hour) — allowed, since only the floor is enforced"
    commission_rate = round(band["commission"](applied_rate), 4)
    fee = round(applied_rate * duration_hours, 2)
    commission = round(fee * commission_rate, 2)
    net = round(fee - commission, 2)
    return {
        "applied_hourly_rate": applied_rate,
        "compliance_note": compliance_note,
        "commission_rate": commission_rate,
        "babysitter_fee": fee,
        "commission_amount": commission,
        "net_to_babysitter": net,
    }


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/register-sitter", status_code=201)
def register_sitter(payload: SitterRegistration):
    cur = db.execute(
        """INSERT INTO babysitters
        (full_name, id_number, phone, email, address, experience_level, years_experience,
         certifications, references_text, availability, bank_name, account_holder,
         account_number, agreed_terms, status, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            payload.full_name, payload.id_number, payload.phone, payload.email, payload.address,
            payload.experience_level, payload.years_experience, payload.certifications,
            payload.references_text, payload.availability, payload.bank_name,
            payload.account_holder, payload.account_number, int(payload.agreed_terms),
            "pending_verification", now_iso(),
        ),
    )
    db.commit()
    return {"id": cur.lastrowid, "status": "pending_verification", "message": "Application received. Our team will contact you to complete SmileID verification."}


@app.post("/api/bookings", status_code=201)
def create_booking(payload: BookingRequest):
    quote = compute_rate_check(payload.level, payload.rate_type, payload.hourly_rate, payload.duration_hours)
    ref = gen_booking_ref()
    pin = gen_pin()
    db.execute(
        """INSERT INTO bookings
        (booking_ref, pin, parent_name, id_number, phone, email, address, children_count,
         booking_date, start_time, rate_type, level, hourly_rate, duration_hours,
         special_instructions, status, agreed_terms, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            ref, pin, payload.parent_name, payload.id_number, payload.phone, payload.email,
            payload.address, payload.children_count, payload.booking_date, payload.start_time,
            payload.rate_type, payload.level, quote["applied_hourly_rate"], payload.duration_hours,
            payload.special_instructions, "pending_match", int(payload.agreed_terms), now_iso(),
        ),
    )
    db.commit()
    return {
        "booking_ref": ref,
        "pin": pin,
        "quote": quote,
        "message": "Booking request received. Save your booking reference and PIN — you and your babysitter will both need them to confirm arrival and departure.",
    }


@app.get("/api/bookings/{booking_ref}")
def get_booking(booking_ref: str, pin: str):
    row = db.execute("SELECT * FROM bookings WHERE booking_ref = ?", (booking_ref,)).fetchone()
    if not row or row["pin"] != pin:
        raise HTTPException(404, "No booking found for that reference and PIN.")
    booking = dict(row)
    checkins = [dict(r) for r in db.execute(
        "SELECT role, action, note, timestamp FROM checkins WHERE booking_ref = ? ORDER BY timestamp",
        (booking_ref,),
    ).fetchall()]
    return {"booking": booking, "checkins": checkins, "summary": summarize_hours(checkins)}


def summarize_hours(checkins):
    latest = {}
    for c in checkins:
        latest[(c["role"], c["action"])] = c["timestamp"]
    sitter_arr = latest.get(("sitter", "arrival"))
    parent_arr = latest.get(("parent", "arrival"))
    sitter_dep = latest.get(("sitter", "departure"))
    parent_dep = latest.get(("parent", "departure"))

    confirmed_start = max(sitter_arr, parent_arr) if sitter_arr and parent_arr else None
    confirmed_end = max(sitter_dep, parent_dep) if sitter_dep and parent_dep else None

    worked_hours = None
    if confirmed_start and confirmed_end:
        start_dt = datetime.fromisoformat(confirmed_start)
        end_dt = datetime.fromisoformat(confirmed_end)
        worked_hours = round((end_dt - start_dt).total_seconds() / 3600, 2)

    def gap_minutes(a, b):
        if not a or not b:
            return None
        return round(abs((datetime.fromisoformat(a) - datetime.fromisoformat(b)).total_seconds() / 60), 1)

    return {
        "sitter_arrival": sitter_arr,
        "parent_arrival": parent_arr,
        "sitter_departure": sitter_dep,
        "parent_departure": parent_dep,
        "arrival_confirmed": bool(sitter_arr and parent_arr),
        "departure_confirmed": bool(sitter_dep and parent_dep),
        "confirmed_start": confirmed_start,
        "confirmed_end": confirmed_end,
        "worked_hours": worked_hours,
        "arrival_gap_minutes": gap_minutes(sitter_arr, parent_arr),
        "departure_gap_minutes": gap_minutes(sitter_dep, parent_dep),
    }


@app.post("/api/checkin", status_code=201)
def checkin(payload: CheckinRequest):
    row = db.execute("SELECT * FROM bookings WHERE booking_ref = ?", (payload.booking_ref,)).fetchone()
    if not row or row["pin"] != payload.pin:
        raise HTTPException(404, "No booking found for that reference and PIN. Double-check both values with the other party.")
    existing = db.execute(
        "SELECT 1 FROM checkins WHERE booking_ref = ? AND role = ? AND action = ?",
        (payload.booking_ref, payload.role, payload.action),
    ).fetchone()
    if existing:
        raise HTTPException(409, f"{payload.role.title()} has already confirmed {payload.action} for this booking.")
    ts = now_iso()
    db.execute(
        "INSERT INTO checkins (booking_ref, role, action, note, timestamp) VALUES (?,?,?,?,?)",
        (payload.booking_ref, payload.role, payload.action, payload.note, ts),
    )
    db.commit()
    checkins = [dict(r) for r in db.execute(
        "SELECT role, action, note, timestamp FROM checkins WHERE booking_ref = ? ORDER BY timestamp",
        (payload.booking_ref,),
    ).fetchall()]
    return {"timestamp": ts, "checkins": checkins, "summary": summarize_hours(checkins)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
