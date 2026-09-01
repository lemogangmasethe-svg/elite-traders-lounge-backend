#!/usr/bin/env python3
"""api_server.py — Elite Traders Lounge backend.

Handles babysitter registration, parent/guardian registration + booking
requests, and the dual (babysitter + parent/guardian) arrival/departure
confirmation system used to track worked hours for every booking.

Runs on port 8000 inside the sandbox.
"""
import base64
import json
import math
import os
import random
import re
import smtplib
import sqlite3
import string
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

import requests
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator, model_validator

import smile_id

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(v: str) -> str:
    if not EMAIL_RE.match(v.strip()):
        raise ValueError("invalid email address")
    return v.strip()


# ---------------------------------------------------------------------------
# Database backend: Postgres (Neon) in production when DATABASE_URL is set,
# SQLite locally/in the sandbox otherwise. Both are exposed through the same
# `db.execute(sql, params)` / `.fetchone()` / `.fetchall()` / `.commit()`
# interface using "?" placeholders, so the route handlers below never need
# to know which backend is active.
# ---------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
USE_POSTGRES = bool(DATABASE_URL)
DB_PATH = "data.db"

SCHEMA_SQL = """
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
    bank_name TEXT NOT NULL DEFAULT '',
    account_holder TEXT NOT NULL DEFAULT '',
    account_number TEXT NOT NULL DEFAULT '',
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

CREATE TABLE IF NOT EXISTS partner_inquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name TEXT NOT NULL,
    property_type TEXT NOT NULL,
    contact_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    city TEXT NOT NULL DEFAULT '',
    message TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS geocode_cache (
    query TEXT PRIMARY KEY,
    lat REAL NOT NULL,
    lon REAL NOT NULL
);
"""

# Columns added after the original launch (identity/verification, proof of
# address, reference/affidavit, and Paystack account details). Applied via
# idempotent ALTER TABLE migrations below so existing rows in both SQLite
# (sandbox preview) and Postgres/Neon (production) keep working.
MIGRATION_COLUMNS = [
    ("babysitters", "id_type", "TEXT NOT NULL DEFAULT 'sa_id'"),
    ("babysitters", "passport_number", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "nationality", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "work_permit_number", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "work_permit_expiry", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "proof_of_address_type", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "proof_of_address_confirmed", "INTEGER NOT NULL DEFAULT 0"),
    ("babysitters", "paystack_email", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "smile_id_consent", "INTEGER NOT NULL DEFAULT 0"),
    ("babysitters", "reference_name", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "reference_relationship", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "reference_phone", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "reference_email", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "reference_affidavit_consent", "INTEGER NOT NULL DEFAULT 0"),
    ("babysitters", "contract_sent", "INTEGER NOT NULL DEFAULT 0"),
    ("bookings", "id_type", "TEXT NOT NULL DEFAULT 'sa_id'"),
    ("bookings", "passport_number", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "nationality", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "proof_of_address_type", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "proof_of_address_confirmed", "INTEGER NOT NULL DEFAULT 0"),
    ("bookings", "paystack_email", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "smile_id_consent", "INTEGER NOT NULL DEFAULT 0"),
    ("bookings", "contract_sent", "INTEGER NOT NULL DEFAULT 0"),
    # Admin dashboard: verification checklists, sitter login codes, and
    # booking -> sitter assignment / accept-decline workflow.
    ("babysitters", "access_code", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "verified", "INTEGER NOT NULL DEFAULT 0"),
    ("babysitters", "id_doc_verified", "INTEGER NOT NULL DEFAULT 0"),
    ("babysitters", "proof_of_address_verified", "INTEGER NOT NULL DEFAULT 0"),
    ("babysitters", "reference_verified", "INTEGER NOT NULL DEFAULT 0"),
    ("babysitters", "smile_id_verified", "INTEGER NOT NULL DEFAULT 0"),
    ("babysitters", "unavailable_dates", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "admin_notes", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "assigned_sitter_id", "INTEGER"),
    ("bookings", "sitter_response", "TEXT NOT NULL DEFAULT 'unassigned'"),
    ("bookings", "family_verified", "INTEGER NOT NULL DEFAULT 0"),
    ("bookings", "family_id_verified", "INTEGER NOT NULL DEFAULT 0"),
    ("bookings", "family_proof_of_address_verified", "INTEGER NOT NULL DEFAULT 0"),
    ("bookings", "admin_notes", "TEXT NOT NULL DEFAULT ''"),
    # Real document uploads (ID document + proof of address) so an admin can
    # view the actual file instead of only relying on a manual attestation.
    # Stored as base64 text — works identically on SQLite and Postgres
    # without needing separate cloud file storage.
    ("babysitters", "id_document_data", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "id_document_filename", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "id_document_mimetype", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "proof_of_address_data", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "proof_of_address_filename", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "proof_of_address_mimetype", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "id_document_data", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "id_document_filename", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "id_document_mimetype", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "proof_of_address_data", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "proof_of_address_filename", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "proof_of_address_mimetype", "TEXT NOT NULL DEFAULT ''"),
    # Parity with babysitters.smile_id_verified — lets admin mark a family's
    # Smile ID step as complete too, once that integration is wired up.
    ("bookings", "family_smile_id_verified", "INTEGER NOT NULL DEFAULT 0"),
    # Selfie + liveness-burst capture (for automatic Smile ID Biometric KYC),
    # a mandatory police clearance certificate upload for babysitters only,
    # and the resulting Smile ID job tracking columns. All stored as base64
    # text like the documents above.
    ("babysitters", "selfie_data", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "selfie_filename", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "selfie_mimetype", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "liveness_images_json", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "police_clearance_data", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "police_clearance_filename", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "police_clearance_mimetype", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "smile_id_job_id", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "smile_id_api_status", "TEXT NOT NULL DEFAULT 'not_configured'"),
    ("babysitters", "smile_id_result_summary", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "smile_id_submitted_at", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "registration_fee_paid", "INTEGER NOT NULL DEFAULT 0"),
    ("bookings", "selfie_data", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "selfie_filename", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "selfie_mimetype", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "liveness_images_json", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "smile_id_job_id", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "smile_id_api_status", "TEXT NOT NULL DEFAULT 'not_configured'"),
    ("bookings", "smile_id_result_summary", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "smile_id_submitted_at", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "registration_fee_paid", "INTEGER NOT NULL DEFAULT 0"),
    # Public babysitter profile (browsable by families once verified) and
    # admin-settable star rating. Profile photo reuses selfie_data —
    # no separate upload column needed, per product decision.
    ("babysitters", "profile_gender", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "profile_race", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "profile_age", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "rating", "REAL NOT NULL DEFAULT 0"),
    # Pet disclosure and in-booking special requests (bathing/feeding/
    # precautions), plus a family's optional preferred-sitter pick — the
    # final assignment is still made by admin via assigned_sitter_id.
    ("bookings", "has_pets", "INTEGER NOT NULL DEFAULT 0"),
    ("bookings", "pet_type", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "special_bath_baby", "INTEGER NOT NULL DEFAULT 0"),
    ("bookings", "special_feed_baby", "INTEGER NOT NULL DEFAULT 0"),
    ("bookings", "special_precautions", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "preferred_sitter_id", "INTEGER"),
    # Marks a booking created directly by admin (phone-in / manual entry,
    # e.g. when the online system is down) rather than submitted by a
    # family through the website.
    ("bookings", "created_by_admin", "INTEGER NOT NULL DEFAULT 0"),
    # Annual re-verification: a Child Protection Register (Part B) clearance
    # is required from every babysitter (separate from the criminal-record
    # police clearance above); a second, foreign police clearance is
    # required only from non-South African babysitters, covering any
    # country they lived in for 12+ months as an adult in the last 5 years.
    # verification_issued_date is the date the current set of documents was
    # accepted — the annual due date is that date + 365 days. fee_paid_at
    # records when the (now annual, not once-off) R99 fee was last
    # confirmed paid, for both babysitters and families.
    ("babysitters", "child_protection_clearance_data", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "child_protection_clearance_filename", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "child_protection_clearance_mimetype", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "foreign_police_clearance_data", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "foreign_police_clearance_filename", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "foreign_police_clearance_mimetype", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "verification_issued_date", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "fee_paid_at", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "fee_paid_at", "TEXT NOT NULL DEFAULT ''"),
    # Location: town/suburb + province the sitter lives in or the family
    # needs care at, plus a geocoded lat/lon so we can calculate real
    # distance and enforce our 40km local service-area rule. lat/lon are
    # nullable — best-effort geocoding must never block a registration or
    # booking on its own.
    ("babysitters", "town", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "province", "TEXT NOT NULL DEFAULT ''"),
    ("babysitters", "lat", "REAL"),
    ("babysitters", "lon", "REAL"),
    ("bookings", "town", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "province", "TEXT NOT NULL DEFAULT ''"),
    ("bookings", "lat", "REAL"),
    ("bookings", "lon", "REAL"),
]

# Document upload constants — used by /api/sitter/documents and
# /api/family/documents. Kept small since files are stored as base64 text.
# "selfie" applies to both sitters and families; "police_clearance" is a
# babysitter-only mandatory upload (SITTER_ONLY_DOCUMENT_KINDS below).
DOCUMENT_KINDS = ("id_document", "proof_of_address", "selfie")
SITTER_ONLY_DOCUMENT_KINDS = ("police_clearance", "child_protection_clearance", "foreign_police_clearance")
MAX_DOCUMENT_BYTES = 6 * 1024 * 1024  # 6MB
ALLOWED_DOCUMENT_MIMETYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "application/pdf"}
ALLOWED_SELFIE_MIMETYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_LIVENESS_FRAMES = 10
MIN_LIVENESS_FRAMES = 3


def run_migrations(conn):
    for table, column, coldef in MIGRATION_COLUMNS:
        try:
            if USE_POSTGRES:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {coldef}")
            else:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coldef}")
        except Exception:
            pass  # column already exists
    conn.commit()


if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras

    class _PgCursor:
        """Wraps a psycopg2 cursor so callers can use dict-style rows and
        .lastrowid the same way the sqlite3 cursor is used elsewhere."""

        def __init__(self, cur, lastrowid=None):
            self._cur = cur
            self.lastrowid = lastrowid

        def fetchone(self):
            row = self._cur.fetchone()
            return dict(row) if row is not None else None

        def fetchall(self):
            return [dict(r) for r in self._cur.fetchall()]

    class _PgConn:
        """Wraps a psycopg2 connection to mimic the sqlite3 connection API
        used by the route handlers (execute/commit/close), translating "?"
        placeholders to "%s" and emulating INSERT ... lastrowid via
        RETURNING id for the tables that need it."""

        def __init__(self, dsn):
            self._dsn = dsn
            self._conn = psycopg2.connect(dsn)

        def _live_conn(self):
            # Neon (and other managed Postgres) can drop idle connections.
            # Reconnect transparently instead of failing every request
            # until the process is restarted.
            if self._conn.closed:
                self._conn = psycopg2.connect(self._dsn)
            return self._conn

        def execute(self, sql, params=()):
            pg_sql = sql.replace("?", "%s")
            needs_id = pg_sql.strip().upper().startswith(
                ("INSERT INTO BABYSITTERS", "INSERT INTO BOOKINGS")
            ) and "RETURNING" not in pg_sql.upper()
            if needs_id:
                pg_sql += " RETURNING id"
            try:
                cur = self._live_conn().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(pg_sql, params)
            except (psycopg2.OperationalError, psycopg2.InterfaceError):
                # Connection was dropped mid-request (e.g. idle timeout) —
                # reconnect once and retry before giving up.
                self._conn = psycopg2.connect(self._dsn)
                cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(pg_sql, params)
            except psycopg2.Error:
                # A prior statement failed and left this shared connection's
                # transaction aborted — roll back so later requests aren't
                # permanently stuck rejecting every query.
                try:
                    self._conn.rollback()
                except Exception:
                    pass
                raise
            lastrowid = None
            if needs_id:
                row = cur.fetchone()
                lastrowid = row["id"] if row else None
            return _PgCursor(cur, lastrowid=lastrowid)

        def executescript(self, script):
            # Translate the SQLite CREATE TABLE statements to Postgres syntax
            # and run each one so new tables are provisioned automatically —
            # avoids tables silently not existing in production until someone
            # remembers to create them by hand on Neon.
            pg_script = script.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            statements = [s.strip() for s in pg_script.split(";") if s.strip()]
            conn = self._live_conn()
            cur = conn.cursor()
            for stmt in statements:
                try:
                    cur.execute(stmt)
                except Exception:
                    conn.rollback()
                else:
                    conn.commit()

        def commit(self):
            self._conn.commit()

        def close(self):
            self._conn.close()

    def get_db():
        return _PgConn(DATABASE_URL)

else:
    def get_db():
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn


db = get_db()
db.executescript(SCHEMA_SQL)
db.commit()
run_migrations(db)


# ---------------------------------------------------------------------------
# Location: turn a town/suburb name into map coordinates (geocoding), work
# out real driving-line distance between two points, and enforce a 40km
# "local service area" so we never promise a family a babysitter who can't
# realistically reach them. Geocoding uses the free OpenStreetMap Nominatim
# service — no account or API key needed. Results are cached in the
# geocode_cache table so we never look up the same town twice.
# ---------------------------------------------------------------------------
LOCAL_RADIUS_KM = 40
GEOCODE_TIMEOUT_SECONDS = 6


def geocode_place(town: str, province: str = "") -> Optional[tuple]:
    """Best-effort lookup of (lat, lon) for a South African town/suburb.
    Returns None if the place can't be found or the lookup fails for any
    reason — callers must treat that as "location unknown", never as a
    hard error, so a slow/unreachable geocoding service never blocks a
    family or sitter from registering."""
    parts = [p.strip() for p in (town, province, "South Africa") if p and p.strip()]
    query = ", ".join(parts)
    if not query or query == "South Africa":
        return None
    cache_key = query.lower()
    try:
        row = db.execute("SELECT lat, lon FROM geocode_cache WHERE query = ?", (cache_key,)).fetchone()
        if row:
            return (row["lat"], row["lon"])
    except Exception:
        pass
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1, "countrycodes": "za"},
            headers={"User-Agent": "EliteTradersLounge/1.0 (lemo.masethe@elitetraders.co.za)"},
            timeout=GEOCODE_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None
        lat, lon = float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        return None
    try:
        db.execute("INSERT INTO geocode_cache (query, lat, lon) VALUES (?, ?, ?)", (cache_key, lat, lon))
        db.commit()
    except Exception:
        pass
    return (lat, lon)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Straight-line distance in kilometres between two lat/lon points."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(min(1.0, a)))


def active_sitters_with_location():
    """Verified babysitters, excluding those whose annual re-verification
    has lapsed, who have a geocoded location on file."""
    rows = [dict(r) for r in db.execute(
        "SELECT id, full_name, town, province, lat, lon, verification_issued_date, created_at "
        "FROM babysitters WHERE verified = 1 AND lat IS NOT NULL AND lon IS NOT NULL"
    ).fetchall()]
    return [
        r for r in rows
        if compute_verification_status(r.get("verification_issued_date", ""), r.get("created_at", "")).get(
            "verification_status"
        ) != "overdue"
    ]


def nearest_sitter_distance(lat: float, lon: float) -> Optional[dict]:
    """Closest active, verified babysitter to a given point. Returns None
    if no verified sitter has a geocoded location yet."""
    best = None
    for sitter in active_sitters_with_location():
        dist = haversine_km(lat, lon, sitter["lat"], sitter["lon"])
        if best is None or dist < best["distance_km"]:
            best = {"distance_km": round(dist, 1), "sitter_id": sitter["id"], "town": sitter["town"]}
    return best


def gen_access_code() -> str:
    for _ in range(20):
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not db.execute("SELECT 1 FROM babysitters WHERE access_code = ?", (code,)).fetchone():
            return code
    raise RuntimeError("could not generate a unique access code")


def backfill_access_codes():
    """Sitters registered before the sitter-login feature existed have no
    access_code yet. Assign one on startup so every sitter can log in."""
    rows = [dict(r) for r in db.execute(
        "SELECT id FROM babysitters WHERE access_code = '' OR access_code IS NULL"
    ).fetchall()]
    for r in rows:
        db.execute("UPDATE babysitters SET access_code = ? WHERE id = ?", (gen_access_code(), r["id"]))
    if rows:
        db.commit()


backfill_access_codes()

# ---------------------------------------------------------------------------
# Admin dashboard auth. A single shared password (set via the ADMIN_PASSWORD
# environment variable in production) protects /api/admin/* endpoints. In
# the sandbox/local dev environment (no DATABASE_URL configured) an
# unconfigured password falls back to a known default so the preview works
# out of the box; production always requires ADMIN_PASSWORD to be set.
# ---------------------------------------------------------------------------
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "").strip()
if not ADMIN_PASSWORD and not USE_POSTGRES:
    ADMIN_PASSWORD = "EliteAdmin2026!"


def require_admin(x_admin_password: str = Header(default="")):
    if not ADMIN_PASSWORD or x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(401, "Incorrect admin password.")
    return True


def authenticate_sitter(email: str, access_code: str) -> dict:
    row = db.execute(
        "SELECT * FROM babysitters WHERE lower(email) = lower(?) AND access_code = ?",
        (email.strip(), access_code.strip().upper()),
    ).fetchone()
    if not row:
        raise HTTPException(401, "That email and access code don't match any registered babysitter.")
    return dict(row)


def sitter_public(row: dict) -> dict:
    result = {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "status": row["status"],
        "verified": bool(row["verified"]),
        "experience_level": row["experience_level"],
        "unavailable_dates": sorted(d for d in (row.get("unavailable_dates") or "").split(",") if d),
        "has_id_document": bool(row.get("id_document_data")),
        "has_proof_of_address": bool(row.get("proof_of_address_data")),
        "id_type": row.get("id_type") or "sa_id",
        "registration_fee_paid": bool(row.get("registration_fee_paid")),
        "fee_paid_at": row.get("fee_paid_at") or "",
    }
    result.update(compute_verification_status(row.get("verification_issued_date", ""), row.get("created_at", "")))
    return result


GENDER_LABELS = {"female": "Female", "male": "Male", "prefer_not_to_say": "Prefer not to say"}
RACE_LABELS = {
    "black_african": "Black African", "coloured": "Coloured", "indian_asian": "Indian / Asian",
    "white": "White", "other": "Other", "prefer_not_to_say": "Prefer not to say",
}


def sitter_public_profile(row: dict, available: Optional[bool] = None, distance_km: Optional[float] = None) -> dict:
    """Public-facing profile shown to families browsing verified babysitters.
    Never includes documents, contact details, or anything beyond what a
    family needs to choose a preferred sitter. `available` is None when no
    booking date/time was supplied to check against (unknown either way).
    `distance_km` is None unless the family's town was supplied and both
    sides have a geocoded location — only the general town/suburb is shared,
    never a full street address."""
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "experience_level": row["experience_level"],
        "years_experience": row["years_experience"],
        "availability": row["availability"],
        "town": row.get("town") or "",
        "nationality": row.get("nationality") or "",
        "profile_gender": GENDER_LABELS.get(row.get("profile_gender") or "", row.get("profile_gender") or ""),
        "profile_race": RACE_LABELS.get(row.get("profile_race") or "", row.get("profile_race") or ""),
        "profile_age": row.get("profile_age") or "",
        "rating": round(row["rating"], 1) if row.get("rating") else None,
        "has_photo": bool(row.get("selfie_data")),
        "photo_url": f"/api/babysitters/{row['id']}/photo" if row.get("selfie_data") else None,
        "available": available,
        "distance_km": distance_km,
        "is_local": (distance_km is not None and distance_km <= LOCAL_RADIUS_KM) if distance_km is not None else None,
        "verification_due_date": compute_verification_status(
            row.get("verification_issued_date", ""), row.get("created_at", "")
        ).get("verification_due_date", ""),
    }


def validate_document_fields(data_b64: str, mimetype: str, filename: str, label: str, allowed_mimetypes=None) -> None:
    """Validate a base64-encoded document upload sent inline with a
    registration/booking payload. Raises ValueError with a friendly message."""
    allowed = allowed_mimetypes or ALLOWED_DOCUMENT_MIMETYPES
    if not (data_b64 or "").strip():
        raise ValueError(f"please upload a copy of your {label}")
    mt = (mimetype or "").lower()
    if mt not in allowed:
        raise ValueError(f"your {label} must be a JPG, PNG, or PDF file")
    try:
        raw = base64.b64decode(data_b64, validate=True)
    except Exception:
        raise ValueError(f"your {label} file could not be read — please try uploading it again")
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise ValueError(f"your {label} file is too large — please upload one under 6MB")
    if not (filename or "").strip():
        raise ValueError(f"your {label} file is missing a filename — please try uploading it again")


def validate_liveness_frames(frames, label: str = "liveness photos") -> None:
    """Validate the burst of liveness-check frames captured from the camera
    widget (a JSON-encoded list of base64 JPEG strings). Raises ValueError
    with a friendly message."""
    if not isinstance(frames, list) or len(frames) < MIN_LIVENESS_FRAMES:
        raise ValueError(f"please complete the {label} capture (turn on your camera and try again)")
    if len(frames) > MAX_LIVENESS_FRAMES:
        frames = frames[:MAX_LIVENESS_FRAMES]
    total_bytes = 0
    for frame in frames:
        try:
            raw = base64.b64decode(frame, validate=True)
        except Exception:
            raise ValueError(f"one of your {label} could not be read — please retake your selfie")
        total_bytes += len(raw)
    if total_bytes > MAX_DOCUMENT_BYTES * 2:
        raise ValueError(f"your {label} capture is too large — please retake your selfie")


def booking_window(date_str: str, time_str: str, duration_hours: float):
    start = datetime.fromisoformat(f"{date_str}T{time_str}")
    end = start + timedelta(hours=duration_hours)
    return start, end


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

LEVELS = {"1", "2", "3", "4"}
# "full_day" is a flat-price alternative to hourly "day" billing — the family
# picks a preset day rate (Appendix C band floor or ceiling × 8 hours) instead
# of typing an hourly rate. It reuses the "day" rate band for that level, so
# it's only available on Levels 1-3, same as hourly day bookings.
RATE_TYPES = {"day", "overnight", "full_day"}
ROLES = {"sitter", "parent"}
ACTIONS = {"arrival", "departure"}

# Appendix C — fixed rates (ZAR) and two-sided commission split, aligned to
# the 2026/2027 National Minimum Wage of R30.23/hour (effective 1 March 2026,
# Government Gazette No. 54075). Each level/booking-type has ONE fixed
# hourly rate (no more negotiated band) and a flat day/night rate. Elite
# Traders Lounge's TOTAL commission is always 20% of the babysitter's fee,
# split between what's added to the Family's bill ("family_pct") and what's
# deducted from the Babysitter's payout ("sitter_pct") — the split differs
# by level, but family_pct + sitter_pct always equals 0.20.
NATIONAL_MINIMUM_WAGE = 30.23

RATE_CARD = {
    ("1", "day"): {"hourly": 45, "flat": 315, "min_hours": 5, "sitter_pct": 0.10, "family_pct": 0.10},
    ("2", "day"): {"hourly": 55, "flat": 385, "min_hours": 5, "sitter_pct": 0.12, "family_pct": 0.08},
    ("3", "day"): {"hourly": 65, "flat": 450, "min_hours": 4, "sitter_pct": 0.125, "family_pct": 0.075},
    ("3", "overnight"): {"hourly": 70, "flat": 700, "min_hours": 10, "sitter_pct": 0.10, "family_pct": 0.10},
    ("4", "overnight"): {"hourly": 85, "flat": 850, "min_hours": 10, "sitter_pct": 0.10, "family_pct": 0.10},
}
# A "full_day" booking is a flat-price alternative to hourly "day" billing —
# 1 day = 7 hours at the level's flat day rate above (day_count multiplies it).
FULL_DAY_HOURS = 7
MIN_HOURS = {
    "day": {level: band["min_hours"] for (level, t), band in RATE_CARD.items() if t == "day"},
    "overnight": {level: band["min_hours"] for (level, t), band in RATE_CARD.items() if t == "overnight"},
    "full_day": FULL_DAY_HOURS,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


VERIFICATION_VALID_DAYS = 365
VERIFICATION_DUE_SOON_DAYS = 30


def compute_verification_status(verification_issued_date: str, created_at: str) -> dict:
    """Annual re-verification tracker for babysitters. A fresh police
    clearance + Child Protection Register check is required every 12
    months; this computes when that's due from whichever date we have —
    the last recorded renewal, or registration date for sitters who
    haven't renewed yet. Returns issued/due dates plus a status label the
    admin and sitter dashboards can colour-code."""
    basis = (verification_issued_date or "").strip()
    if not basis and created_at:
        basis = created_at[:10]
    if not basis:
        return {"verification_issued_date": "", "verification_due_date": "", "verification_status": "unknown"}
    try:
        issued = datetime.fromisoformat(basis[:10])
    except ValueError:
        return {"verification_issued_date": basis, "verification_due_date": "", "verification_status": "unknown"}
    due = issued + timedelta(days=VERIFICATION_VALID_DAYS)
    today = datetime.now(timezone.utc).replace(tzinfo=None)
    days_left = (due - today).days
    if days_left < 0:
        status = "overdue"
    elif days_left <= VERIFICATION_DUE_SOON_DAYS:
        status = "due_soon"
    else:
        status = "current"
    return {
        "verification_issued_date": basis,
        "verification_due_date": due.strftime("%Y-%m-%d"),
        "verification_status": status,
        "verification_days_left": days_left,
    }


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
    id_type: str = "sa_id"
    id_number: Optional[str] = Field(default="", max_length=20)
    passport_number: Optional[str] = ""
    nationality: Optional[str] = ""
    work_permit_number: Optional[str] = ""
    work_permit_expiry: Optional[str] = ""
    phone: str = Field(min_length=7, max_length=20)
    email: str
    address: str = Field(min_length=5, max_length=300)
    town: str = Field(min_length=2, max_length=80)
    province: str = Field(min_length=2, max_length=40)
    proof_of_address_type: str = Field(min_length=2, max_length=60)
    proof_of_address_confirmed: bool
    experience_level: str
    years_experience: str
    certifications: Optional[str] = ""
    reference_name: str = Field(min_length=2, max_length=120)
    reference_relationship: str = Field(min_length=2, max_length=80)
    reference_phone: str = Field(min_length=7, max_length=20)
    reference_email: str
    reference_affidavit_consent: bool
    availability: str = Field(min_length=2, max_length=300)
    profile_gender: str = Field(min_length=1, max_length=30)
    profile_race: str = Field(min_length=1, max_length=30)
    profile_age: int = Field(ge=18, le=80)
    paystack_email: str
    smile_id_consent: bool
    bank_name: Optional[str] = ""
    account_holder: Optional[str] = ""
    account_number: Optional[str] = ""
    agreed_terms: bool
    id_document_data: str = Field(default="")
    id_document_filename: str = Field(default="")
    id_document_mimetype: str = Field(default="")
    proof_of_address_data: str = Field(default="")
    proof_of_address_filename: str = Field(default="")
    proof_of_address_mimetype: str = Field(default="")
    selfie_data: str = Field(default="")
    selfie_filename: str = Field(default="")
    selfie_mimetype: str = Field(default="")
    liveness_images: list = Field(default_factory=list)
    police_clearance_data: str = Field(default="")
    police_clearance_filename: str = Field(default="")
    police_clearance_mimetype: str = Field(default="")
    child_protection_clearance_data: str = Field(default="")
    child_protection_clearance_filename: str = Field(default="")
    child_protection_clearance_mimetype: str = Field(default="")
    foreign_police_clearance_data: str = Field(default="")
    foreign_police_clearance_filename: str = Field(default="")
    foreign_police_clearance_mimetype: str = Field(default="")

    _validate_email = field_validator("email")(validate_email)
    _validate_reference_email = field_validator("reference_email")(validate_email)
    _validate_paystack_email = field_validator("paystack_email")(validate_email)

    @field_validator("experience_level")
    @classmethod
    def check_level(cls, v):
        if v not in LEVELS:
            raise ValueError("experience_level must be 1, 2, 3 or 4")
        return v

    @field_validator("id_type")
    @classmethod
    def check_id_type(cls, v):
        if v not in {"sa_id", "passport"}:
            raise ValueError("id_type must be 'sa_id' or 'passport'")
        return v

    @model_validator(mode="after")
    def check_id_fields(self):
        if not (self.nationality or "").strip():
            raise ValueError("nationality is required")
        if self.id_type == "passport":
            missing = [
                name for name in ("passport_number", "work_permit_number", "work_permit_expiry")
                if not (getattr(self, name) or "").strip()
            ]
            if missing:
                raise ValueError(
                    "passport and a valid work permit number + expiry date are required for "
                    "non-South African freelance babysitters to stay compliant with SA immigration law"
                )
        else:
            if len((self.id_number or "").strip()) < 5:
                raise ValueError("a valid South African ID number (at least 5 characters) is required")
        return self

    @field_validator("profile_gender")
    @classmethod
    def check_profile_gender(cls, v):
        if v not in GENDER_LABELS:
            raise ValueError("please select a gender option")
        return v

    @field_validator("profile_race")
    @classmethod
    def check_profile_race(cls, v):
        if v not in RACE_LABELS:
            raise ValueError("please select a race/ethnicity option")
        return v

    @field_validator("proof_of_address_confirmed")
    @classmethod
    def check_poa(cls, v):
        if not v:
            raise ValueError("you must confirm your proof of address document matches your registered address")
        return v

    @field_validator("reference_affidavit_consent")
    @classmethod
    def check_affidavit(cls, v):
        if not v:
            raise ValueError("you must consent to your reference being contacted and to swearing the reference affidavit")
        return v

    @field_validator("smile_id_consent")
    @classmethod
    def check_smile_id(cls, v):
        if not v:
            raise ValueError("you must consent to Smile ID identity verification to register")
        return v

    @field_validator("agreed_terms")
    @classmethod
    def check_agreed(cls, v):
        if not v:
            raise ValueError("you must accept the babysitter contract terms to register")
        return v

    @model_validator(mode="after")
    def check_documents(self):
        validate_document_fields(self.id_document_data, self.id_document_mimetype, self.id_document_filename, "ID document")
        validate_document_fields(self.proof_of_address_data, self.proof_of_address_mimetype, self.proof_of_address_filename, "proof of address")
        validate_document_fields(self.selfie_data, self.selfie_mimetype, self.selfie_filename, "selfie photo", ALLOWED_SELFIE_MIMETYPES)
        validate_liveness_frames(self.liveness_images)
        validate_document_fields(
            self.police_clearance_data, self.police_clearance_mimetype, self.police_clearance_filename,
            "police clearance certificate",
        )
        validate_document_fields(
            self.child_protection_clearance_data, self.child_protection_clearance_mimetype,
            self.child_protection_clearance_filename, "Child Protection Register (Part B) clearance letter",
        )
        if self.id_type == "passport":
            validate_document_fields(
                self.foreign_police_clearance_data, self.foreign_police_clearance_mimetype,
                self.foreign_police_clearance_filename,
                "foreign police clearance certificate",
            )
        return self


class BookingRequest(BaseModel):
    parent_name: str = Field(min_length=2, max_length=120)
    id_type: str = "sa_id"
    id_number: Optional[str] = Field(default="", max_length=20)
    passport_number: Optional[str] = ""
    nationality: Optional[str] = ""
    phone: str = Field(min_length=7, max_length=20)
    email: str
    address: str = Field(min_length=5, max_length=300)
    town: str = Field(min_length=2, max_length=80)
    province: str = Field(min_length=2, max_length=40)
    proof_of_address_type: str = Field(min_length=2, max_length=60)
    proof_of_address_confirmed: bool
    children_count: str = Field(min_length=1, max_length=20)
    paystack_email: str
    smile_id_consent: bool

    _validate_email = field_validator("email")(validate_email)
    _validate_paystack_email = field_validator("paystack_email")(validate_email)
    booking_date: str
    start_time: str
    rate_type: str
    level: str
    hourly_rate: float = Field(gt=0)
    duration_hours: float = Field(gt=0)
    special_instructions: Optional[str] = ""
    has_pets: bool = False
    pet_type: Optional[str] = Field(default="", max_length=200)
    special_bath_baby: bool = False
    special_feed_baby: bool = False
    special_precautions: Optional[str] = Field(default="", max_length=1000)
    preferred_sitter_id: Optional[int] = None
    agreed_terms: bool
    id_document_data: str = Field(default="")
    id_document_filename: str = Field(default="")
    id_document_mimetype: str = Field(default="")
    proof_of_address_data: str = Field(default="")
    proof_of_address_filename: str = Field(default="")
    proof_of_address_mimetype: str = Field(default="")
    selfie_data: str = Field(default="")
    selfie_filename: str = Field(default="")
    selfie_mimetype: str = Field(default="")
    liveness_images: list = Field(default_factory=list)

    @model_validator(mode="after")
    def check_pet_type(self):
        if self.has_pets and not (self.pet_type or "").strip():
            raise ValueError("please tell us what type of pet(s) you have")
        return self

    @field_validator("level")
    @classmethod
    def check_level(cls, v):
        if v not in LEVELS:
            raise ValueError("level must be 1, 2, 3 or 4")
        return v

    @field_validator("id_type")
    @classmethod
    def check_id_type(cls, v):
        if v not in {"sa_id", "passport"}:
            raise ValueError("id_type must be 'sa_id' or 'passport'")
        return v

    @model_validator(mode="after")
    def check_id_fields(self):
        if self.id_type == "passport":
            missing = [
                name for name in ("passport_number", "nationality")
                if not (getattr(self, name) or "").strip()
            ]
            if missing:
                raise ValueError("passport number and nationality are required for passport holders")
        else:
            if len((self.id_number or "").strip()) < 5:
                raise ValueError("a valid South African ID number (at least 5 characters) is required")
        return self

    @field_validator("proof_of_address_confirmed")
    @classmethod
    def check_poa(cls, v):
        if not v:
            raise ValueError("you must confirm your proof of address document matches your registered address")
        return v

    @field_validator("smile_id_consent")
    @classmethod
    def check_smile_id(cls, v):
        if not v:
            raise ValueError("you must consent to Smile ID identity verification to book a sitter")
        return v

    @field_validator("rate_type")
    @classmethod
    def check_rate_type(cls, v):
        if v not in RATE_TYPES:
            raise ValueError("rate_type must be 'day', 'overnight', or 'full_day'")
        return v

    @field_validator("agreed_terms")
    @classmethod
    def check_agreed(cls, v):
        if not v:
            raise ValueError("you must accept the booking contract terms to submit a booking")
        return v

    @model_validator(mode="after")
    def check_documents(self):
        validate_document_fields(self.id_document_data, self.id_document_mimetype, self.id_document_filename, "ID document")
        validate_document_fields(self.proof_of_address_data, self.proof_of_address_mimetype, self.proof_of_address_filename, "proof of address")
        validate_document_fields(self.selfie_data, self.selfie_mimetype, self.selfie_filename, "selfie photo", ALLOWED_SELFIE_MIMETYPES)
        validate_liveness_frames(self.liveness_images)
        return self


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
    # "full_day" is a flat-price booking (the level's flat day rate ×
    # 7-hour blocks) that reuses the "day" rate card entry for that level for
    # commission purposes — only the label and minimum-hours check differ.
    band_lookup_type = "day" if rate_type == "full_day" else rate_type
    band = RATE_CARD.get((level, band_lookup_type))
    if band is None:
        raise HTTPException(422, f"Level {level} has no {rate_type} rate. Level 1 and 2 are day/full-day only; Level 3 supports day, full-day, and overnight; Level 4 is overnight/specialist only.")
    if rate_type == "full_day":
        min_hours = FULL_DAY_HOURS
        if duration_hours < min_hours or duration_hours % min_hours != 0:
            raise HTTPException(422, f"Full-day bookings are billed in {min_hours}-hour blocks (1 day = {min_hours} hours, 2 days = {min_hours * 2} hours, etc.).")
    else:
        min_hours = band["min_hours"]
        if duration_hours < min_hours:
            raise HTTPException(422, f"Minimum booking length for a Level {level} {rate_type} booking is {min_hours} hours.")
    # Rates are fixed by level/type — there is no negotiated band anymore.
    # The server always applies the fixed Appendix C rate; whatever the
    # client sends in hourly_rate is informational only and never used.
    applied_rate = band["hourly"]
    compliance_note = f"fixed Level {level} {rate_type} rate applied per Appendix C"
    if applied_rate < NATIONAL_MINIMUM_WAGE:
        applied_rate = NATIONAL_MINIMUM_WAGE
        compliance_note = f"Level {level} {rate_type} rate was below the National Minimum Wage (R{NATIONAL_MINIMUM_WAGE}/hour) — automatically corrected to R{applied_rate}/hour"
    if rate_type == "full_day":
        day_count = duration_hours / FULL_DAY_HOURS
        fee = round(band["flat"] * day_count, 2)
    else:
        fee = round(applied_rate * duration_hours, 2)
    # Two-sided commission: Elite Traders Lounge's TOTAL commission is
    # always 20% of the babysitter's fee, split unevenly — part is added on
    # top of what the Family pays, part is deducted from the Babysitter's
    # payout. The two percentages differ by level but always sum to 20%.
    sitter_rate = band["sitter_pct"]
    family_rate = band["family_pct"]
    total_commission_rate = round(sitter_rate + family_rate, 4)
    family_commission_amount = round(fee * family_rate, 2)
    family_total = round(fee + family_commission_amount, 2)
    sitter_commission_amount = round(fee * sitter_rate, 2)
    net_to_babysitter = round(fee - sitter_commission_amount, 2)
    return {
        "applied_hourly_rate": applied_rate,
        "compliance_note": compliance_note,
        "commission_rate": total_commission_rate,
        "family_commission_rate": family_rate,
        "sitter_commission_rate": sitter_rate,
        "babysitter_fee": fee,
        "family_commission_amount": family_commission_amount,
        "family_total": family_total,
        "commission_amount": sitter_commission_amount,
        "sitter_commission_amount": sitter_commission_amount,
        "net_to_babysitter": net_to_babysitter,
    }


# ---------------------------------------------------------------------------
# Contract PDF delivery: served as static downloads and, when SMTP env vars
# are configured, emailed to the registrant on submission. Missing SMTP
# config degrades gracefully — registration/booking still succeeds and the
# contract remains available as a direct download link.
# ---------------------------------------------------------------------------
CONTRACTS_DIR = Path(__file__).resolve().parent / "assets" / "contracts"
CONTRACT_FILES = {
    "sitter": "elite-traders-lounge-babysitter-agreement-2026.pdf",
    "family": "elite-traders-lounge-family-agreement-2026.pdf",
}
if CONTRACTS_DIR.exists():
    app.mount("/contracts", StaticFiles(directory=str(CONTRACTS_DIR)), name="contracts")

SMTP_HOST = os.environ.get("SMTP_HOST", "").strip()
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587") or "587")
SMTP_USER = os.environ.get("SMTP_USER", "").strip()
SMTP_PASS = os.environ.get("SMTP_PASS", "").strip()
EMAIL_FROM = os.environ.get("EMAIL_FROM", "").strip() or SMTP_USER


def contract_url_for(kind: str) -> Optional[str]:
    filename = CONTRACT_FILES.get(kind)
    if not filename or not (CONTRACTS_DIR / filename).exists():
        return None
    return f"/contracts/{filename}"


def send_contract_email(to_email: str, recipient_name: str, kind: str) -> bool:
    """Best-effort email of the signed-ready contract PDF. Returns True only
    if the message was actually sent. Never raises — SMTP not being
    configured (or failing) must not block registration/booking."""
    filename = CONTRACT_FILES.get(kind)
    if not filename or not SMTP_HOST or not SMTP_USER or not SMTP_PASS or not EMAIL_FROM:
        return False
    pdf_path = CONTRACTS_DIR / filename
    if not pdf_path.exists():
        return False
    try:
        label = "Babysitter Service Agreement" if kind == "sitter" else "Family Service Agreement"
        msg = EmailMessage()
        msg["Subject"] = f"Elite Traders Lounge — Your {label} (2026)"
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email
        msg.set_content(
            f"Hi {recipient_name},\n\n"
            f"Thank you for registering with Elite Traders Lounge. Attached is your {label} for 2026, "
            "covering rates, the commission structure, cancellation policy, identity verification, and "
            "Paystack Split Payment details.\n\n"
            "Please read it in full. Continuing to use the platform after registration constitutes your "
            "acceptance of these terms (see Section 16, Digital Signatures, in the agreement, and our "
            "Terms & Conditions at /terms.html).\n\n"
            "Elite Traders Lounge (Reg. K2017318876)\n"
            "lemo.masethe@elitetraders.co.za | +27 81 427 0419"
        )
        msg.add_attachment(
            pdf_path.read_bytes(), maintype="application", subtype="pdf", filename=filename
        )
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception:
        return False


@app.get("/api/health")
def health():
    return {"ok": True}


class PartnerInquiry(BaseModel):
    business_name: str = Field(min_length=2, max_length=150)
    property_type: str = Field(min_length=2, max_length=40)
    contact_name: str = Field(min_length=2, max_length=120)
    email: str
    phone: str = Field(min_length=7, max_length=20)
    city: Optional[str] = ""
    message: Optional[str] = Field(default="", max_length=1000)

    @field_validator("email")
    @classmethod
    def check_email(cls, v):
        return validate_email(v)


def send_partner_inquiry_email(inquiry: PartnerInquiry) -> bool:
    """Best-effort notification email to Elite Traders Lounge when a hotel,
    guesthouse, or Airbnb/BnB host submits a partnership inquiry. Never
    raises — the inquiry is already saved to the database regardless of
    whether this email succeeds."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS or not EMAIL_FROM:
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = f"New partner inquiry — {inquiry.business_name}"
        msg["From"] = EMAIL_FROM
        msg["To"] = "lemo.masethe@elitetraders.co.za"
        msg["Reply-To"] = inquiry.email
        msg.set_content(
            "A hotel/guesthouse/Airbnb host has asked to partner with Elite Traders Lounge.\n\n"
            f"Business / property name: {inquiry.business_name}\n"
            f"Property type: {inquiry.property_type}\n"
            f"Contact name: {inquiry.contact_name}\n"
            f"Email: {inquiry.email}\n"
            f"Phone: {inquiry.phone}\n"
            f"City: {inquiry.city or '—'}\n\n"
            f"Message:\n{inquiry.message or '(no message provided)'}\n"
        )
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception:
        return False


@app.post("/api/partner-inquiries", status_code=201)
def create_partner_inquiry(payload: PartnerInquiry):
    db.execute(
        "INSERT INTO partner_inquiries (business_name, property_type, contact_name, email, phone, city, "
        "message, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            payload.business_name.strip(), payload.property_type.strip(), payload.contact_name.strip(),
            payload.email.strip(), payload.phone.strip(), (payload.city or "").strip(),
            (payload.message or "").strip(), now_iso(),
        ),
    )
    db.commit()
    send_partner_inquiry_email(payload)
    return {"ok": True}


def _run_smile_id_submission(*, table: str, row_id: int, kind: str, full_name: str, email: str, phone: str,
                              id_type: str, id_number: str, selfie_data: str, liveness_images: list) -> None:
    """Best-effort automatic Smile ID submission. Never raises — failures are
    stored on the row as an "error" status so admin can see them, but the
    registration/booking itself always succeeds regardless of Smile ID."""
    try:
        result = smile_id.submit_biometric_kyc(
            user_id=f"{kind}-{row_id}",
            job_id=f"{kind}-{row_id}-{int(datetime.now(timezone.utc).timestamp())}",
            full_name=full_name,
            email=email,
            phone=phone,
            id_type=id_type,
            id_number=id_number,
            selfie_bytes=base64.b64decode(selfie_data),
            liveness_bytes_list=[base64.b64decode(f) for f in liveness_images],
        )
    except Exception as exc:  # noqa: BLE001 — best-effort by design
        result = {"status": "error", "message": str(exc)}
    db.execute(
        f"UPDATE {table} SET smile_id_job_id = ?, smile_id_api_status = ?, "
        f"smile_id_result_summary = ?, smile_id_submitted_at = ? WHERE id = ?",
        (
            result.get("job_id", ""), result.get("status", "error"),
            result.get("message", ""), now_iso(), row_id,
        ),
    )
    db.commit()


@app.post("/api/register-sitter", status_code=201)
def register_sitter(payload: SitterRegistration):
    emailed = send_contract_email(payload.email, payload.full_name, "sitter")
    access_code = gen_access_code()
    liveness_json = json.dumps(payload.liveness_images)
    geocoded = geocode_place(payload.town, payload.province)
    lat, lon = geocoded if geocoded else (None, None)
    cur = db.execute(
        """INSERT INTO babysitters
        (full_name, id_type, id_number, passport_number, nationality, work_permit_number,
         work_permit_expiry, phone, email, address, town, province, lat, lon, proof_of_address_type,
         proof_of_address_confirmed, experience_level, years_experience, certifications,
         references_text, availability, reference_name, reference_relationship,
         reference_phone, reference_email, reference_affidavit_consent, paystack_email,
         smile_id_consent, bank_name, account_holder, account_number, agreed_terms,
         contract_sent, access_code, status, created_at,
         id_document_data, id_document_filename, id_document_mimetype,
         proof_of_address_data, proof_of_address_filename, proof_of_address_mimetype,
         selfie_data, selfie_filename, selfie_mimetype, liveness_images_json,
         police_clearance_data, police_clearance_filename, police_clearance_mimetype,
         child_protection_clearance_data, child_protection_clearance_filename, child_protection_clearance_mimetype,
         foreign_police_clearance_data, foreign_police_clearance_filename, foreign_police_clearance_mimetype,
         verification_issued_date,
         profile_gender, profile_race, profile_age)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            payload.full_name, payload.id_type, payload.id_number, payload.passport_number,
            payload.nationality, payload.work_permit_number, payload.work_permit_expiry,
            payload.phone, payload.email, payload.address, payload.town, payload.province, lat, lon,
            payload.proof_of_address_type,
            int(payload.proof_of_address_confirmed), payload.experience_level,
            payload.years_experience, payload.certifications,
            f"{payload.reference_name} ({payload.reference_relationship}) — {payload.reference_phone}, {payload.reference_email}",
            payload.availability, payload.reference_name, payload.reference_relationship,
            payload.reference_phone, payload.reference_email, int(payload.reference_affidavit_consent),
            payload.paystack_email, int(payload.smile_id_consent), payload.bank_name,
            payload.account_holder, payload.account_number, int(payload.agreed_terms),
            int(emailed), access_code, "pending_verification", now_iso(),
            payload.id_document_data, payload.id_document_filename, payload.id_document_mimetype,
            payload.proof_of_address_data, payload.proof_of_address_filename, payload.proof_of_address_mimetype,
            payload.selfie_data, payload.selfie_filename, payload.selfie_mimetype, liveness_json,
            payload.police_clearance_data, payload.police_clearance_filename, payload.police_clearance_mimetype,
            payload.child_protection_clearance_data, payload.child_protection_clearance_filename,
            payload.child_protection_clearance_mimetype,
            payload.foreign_police_clearance_data, payload.foreign_police_clearance_filename,
            payload.foreign_police_clearance_mimetype,
            now_iso()[:10],
            payload.profile_gender, payload.profile_race, str(payload.profile_age),
        ),
    )
    db.commit()
    sitter_id = cur.lastrowid
    _run_smile_id_submission(
        table="babysitters", row_id=sitter_id, kind="sitter",
        full_name=payload.full_name, email=payload.email, phone=payload.phone,
        id_type=payload.id_type, id_number=payload.id_number or payload.passport_number,
        selfie_data=payload.selfie_data, liveness_images=payload.liveness_images,
    )
    return {
        "id": sitter_id,
        "access_code": access_code,
        "status": "pending_verification",
        "contract_url": contract_url_for("sitter"),
        "contract_emailed": emailed,
        "message": (
            "Application received. Our team will contact you to complete Smile ID verification and confirm "
            "your reference/affidavit. "
            + ("Your Babysitter Service Agreement has been emailed to you." if emailed
               else "Download your Babysitter Service Agreement below — we'll also email a copy once it's ready.")
        ),
    }


@app.post("/api/bookings", status_code=201)
def create_booking(payload: BookingRequest):
    quote = compute_rate_check(payload.level, payload.rate_type, payload.hourly_rate, payload.duration_hours)
    ref = gen_booking_ref()
    pin = gen_pin()
    if payload.preferred_sitter_id is not None:
        row = db.execute(
            "SELECT id FROM babysitters WHERE id = ? AND verified = 1", (payload.preferred_sitter_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="the preferred babysitter you selected is no longer available")
    # Local service-area rule: we only accept bookings where at least one
    # verified, active babysitter is within LOCAL_RADIUS_KM — we can't
    # promise a family a sitter who can't realistically travel to them. If
    # we can't geocode the town at all, let the booking through rather than
    # block a real family over a geocoding hiccup; admin can still review it.
    geocoded = geocode_place(payload.town, payload.province)
    lat, lon = geocoded if geocoded else (None, None)
    if geocoded:
        nearest = nearest_sitter_distance(lat, lon)
        if nearest is None or nearest["distance_km"] > LOCAL_RADIUS_KM:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"We don't currently have a verified babysitter within {LOCAL_RADIUS_KM}km of "
                    f"{payload.town.strip()} — Elite Traders Lounge can only confirm bookings in areas our "
                    "babysitters can reach. Please contact us at lemo.masethe@elitetraders.co.za or "
                    "081 427 0419 so we can look into registering a sitter closer to you."
                ),
            )
    emailed = send_contract_email(payload.email, payload.parent_name, "family")
    liveness_json = json.dumps(payload.liveness_images)
    cur = db.execute(
        """INSERT INTO bookings
        (booking_ref, pin, parent_name, id_type, id_number, passport_number, nationality,
         phone, email, address, town, province, lat, lon, proof_of_address_type, proof_of_address_confirmed,
         children_count, paystack_email, smile_id_consent, booking_date, start_time,
         rate_type, level, hourly_rate, duration_hours, special_instructions, status,
         agreed_terms, contract_sent, created_at,
         id_document_data, id_document_filename, id_document_mimetype,
         proof_of_address_data, proof_of_address_filename, proof_of_address_mimetype,
         selfie_data, selfie_filename, selfie_mimetype, liveness_images_json,
         has_pets, pet_type, special_bath_baby, special_feed_baby, special_precautions,
         preferred_sitter_id)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            ref, pin, payload.parent_name, payload.id_type, payload.id_number,
            payload.passport_number, payload.nationality, payload.phone, payload.email,
            payload.address, payload.town, payload.province, lat, lon,
            payload.proof_of_address_type, int(payload.proof_of_address_confirmed),
            payload.children_count, payload.paystack_email, int(payload.smile_id_consent),
            payload.booking_date, payload.start_time, payload.rate_type, payload.level,
            quote["applied_hourly_rate"], payload.duration_hours, payload.special_instructions,
            "pending_match", int(payload.agreed_terms), int(emailed), now_iso(),
            payload.id_document_data, payload.id_document_filename, payload.id_document_mimetype,
            payload.proof_of_address_data, payload.proof_of_address_filename, payload.proof_of_address_mimetype,
            payload.selfie_data, payload.selfie_filename, payload.selfie_mimetype, liveness_json,
            int(payload.has_pets), payload.pet_type, int(payload.special_bath_baby),
            int(payload.special_feed_baby), payload.special_precautions, payload.preferred_sitter_id,
        ),
    )
    db.commit()
    _run_smile_id_submission(
        table="bookings", row_id=cur.lastrowid, kind="family",
        full_name=payload.parent_name, email=payload.email, phone=payload.phone,
        id_type=payload.id_type, id_number=payload.id_number or payload.passport_number,
        selfie_data=payload.selfie_data, liveness_images=payload.liveness_images,
    )
    return {
        "booking_ref": ref,
        "pin": pin,
        "quote": quote,
        "contract_url": contract_url_for("family"),
        "contract_emailed": emailed,
        "message": (
            "Booking request received. Save your booking reference and PIN — you and your babysitter will both "
            "need them to confirm arrival and departure. "
            + ("Your Family Service Agreement has been emailed to you." if emailed
               else "Download your Family Service Agreement below — we'll also email a copy once it's ready.")
        ),
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


# ---------------------------------------------------------------------------
# Admin dashboard API — password-protected via the X-Admin-Password header.
# ---------------------------------------------------------------------------
class AdminLoginRequest(BaseModel):
    password: str


@app.post("/api/admin/login")
def admin_login(payload: AdminLoginRequest):
    if not ADMIN_PASSWORD or payload.password != ADMIN_PASSWORD:
        raise HTTPException(401, "Incorrect admin password.")
    return {"ok": True}


def strip_document_blobs(row: dict, extra_kinds=()) -> dict:
    """Replace large base64 document blobs with lightweight has_x/filename
    flags before sending a list of rows to the admin dashboard."""
    for kind in (*DOCUMENT_KINDS, *extra_kinds):
        data_key = f"{kind}_data"
        row[f"has_{kind}"] = bool(row.get(data_key))
        row.pop(data_key, None)
    liveness = row.pop("liveness_images_json", None)
    if liveness is not None:
        try:
            row["liveness_frame_count"] = len(json.loads(liveness) or [])
        except Exception:
            row["liveness_frame_count"] = 0
    return row


@app.get("/api/admin/sitters")
def admin_list_sitters(admin_ok: bool = Depends(require_admin)):
    rows = [dict(r) for r in db.execute("SELECT * FROM babysitters ORDER BY created_at DESC").fetchall()]
    for r in rows:
        r.update(compute_verification_status(r.get("verification_issued_date", ""), r.get("created_at", "")))
    rows = [strip_document_blobs(r, extra_kinds=SITTER_ONLY_DOCUMENT_KINDS) for r in rows]
    return {"sitters": rows}


@app.get("/api/admin/sitters/{sitter_id}/document/{document_type}")
def admin_get_sitter_document(sitter_id: int, document_type: str, admin_ok: bool = Depends(require_admin)):
    if document_type not in (*DOCUMENT_KINDS, *SITTER_ONLY_DOCUMENT_KINDS):
        raise HTTPException(400, "Unknown document type.")
    row = db.execute(
        f"SELECT {document_type}_data AS data, {document_type}_filename AS filename, "
        f"{document_type}_mimetype AS mimetype FROM babysitters WHERE id = ?",
        (sitter_id,),
    ).fetchone()
    if not row or not row["data"]:
        raise HTTPException(404, "That sitter hasn't uploaded this document yet.")
    raw = base64.b64decode(row["data"])
    filename = row["filename"] or document_type
    return Response(
        content=raw,
        media_type=row["mimetype"] or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


class AdminSitterVerifyRequest(BaseModel):
    id_doc_verified: bool = False
    proof_of_address_verified: bool = False
    reference_verified: bool = False
    smile_id_verified: bool = False
    registration_fee_paid: bool = False
    admin_notes: Optional[str] = ""
    rating: Optional[float] = None
    # Optional admin backfill for sitters who registered before the public
    # profile fields existed. Left unset (None) means "don't change".
    profile_gender: Optional[str] = None
    profile_race: Optional[str] = None
    profile_age: Optional[int] = None
    # Optional admin control: set/reset the date the current police
    # clearance + Child Protection Register documents were accepted. This
    # resets the 12-month annual re-verification clock. Leave unset (None)
    # to keep the existing date unchanged.
    verification_issued_date: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def check_rating(cls, v):
        if v is not None and not (0 <= v <= 5):
            raise ValueError("rating must be between 0 and 5")
        return v

    @field_validator("profile_gender")
    @classmethod
    def check_admin_profile_gender(cls, v):
        if v is not None and v != "" and v not in GENDER_LABELS:
            raise ValueError("profile_gender must be one of: " + ", ".join(GENDER_LABELS))
        return v

    @field_validator("profile_race")
    @classmethod
    def check_admin_profile_race(cls, v):
        if v is not None and v != "" and v not in RACE_LABELS:
            raise ValueError("profile_race must be one of: " + ", ".join(RACE_LABELS))
        return v

    @field_validator("profile_age")
    @classmethod
    def check_admin_profile_age(cls, v):
        if v is not None and not (18 <= v <= 80):
            raise ValueError("profile_age must be between 18 and 80")
        return v


@app.post("/api/admin/sitters/{sitter_id}/verify")
def admin_verify_sitter(sitter_id: int, payload: AdminSitterVerifyRequest, admin_ok: bool = Depends(require_admin)):
    row = db.execute(
        "SELECT id, rating, profile_gender, profile_race, profile_age, registration_fee_paid, fee_paid_at, "
        "verification_issued_date FROM babysitters WHERE id = ?", (sitter_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, "Sitter not found.")
    verified = (
        payload.id_doc_verified and payload.proof_of_address_verified
        and payload.reference_verified and payload.smile_id_verified
    )
    status = "verified" if verified else "pending_verification"
    rating = payload.rating if payload.rating is not None else row["rating"]
    # Admin can backfill the public profile fields for sitters who registered
    # before these existed (e.g. earlier test/real signups) — only overwrite
    # when a non-empty value is explicitly sent.
    profile_gender = payload.profile_gender if payload.profile_gender else row["profile_gender"]
    profile_race = payload.profile_race if payload.profile_race else row["profile_race"]
    profile_age = str(payload.profile_age) if payload.profile_age else row["profile_age"]
    # The R99 fee is now annual, not once-off: stamp today's date the moment
    # admin flips it from unpaid to paid, so both admin and the sitter can
    # see when it was last paid. Unticking it clears the stamp.
    was_paid = bool(row["registration_fee_paid"])
    if payload.registration_fee_paid and not was_paid:
        fee_paid_at = now_iso()[:10]
    elif payload.registration_fee_paid:
        fee_paid_at = row["fee_paid_at"] or now_iso()[:10]
    else:
        fee_paid_at = ""
    verification_issued_date = (
        payload.verification_issued_date if payload.verification_issued_date is not None
        else row["verification_issued_date"]
    )
    db.execute(
        """UPDATE babysitters SET id_doc_verified=?, proof_of_address_verified=?, reference_verified=?,
        smile_id_verified=?, registration_fee_paid=?, fee_paid_at=?, verified=?, status=?, admin_notes=?, rating=?,
        profile_gender=?, profile_race=?, profile_age=?, verification_issued_date=? WHERE id=?""",
        (
            int(payload.id_doc_verified), int(payload.proof_of_address_verified),
            int(payload.reference_verified), int(payload.smile_id_verified),
            int(payload.registration_fee_paid), fee_paid_at,
            int(verified), status, payload.admin_notes or "", rating,
            profile_gender, profile_race, profile_age, verification_issued_date, sitter_id,
        ),
    )
    db.commit()
    return {"id": sitter_id, "verified": verified, "status": status, "rating": rating}


@app.get("/api/babysitters/public")
def list_public_babysitters(
    date: Optional[str] = None, start_time: Optional[str] = None, duration_hours: Optional[float] = None,
    town: Optional[str] = None, province: Optional[str] = None,
):
    """Families browse verified, identity-checked babysitters. If a booking
    date/time/duration is supplied, each sitter is flagged available or not
    for that specific slot (checked against their marked-unavailable dates
    and any clashing accepted bookings) so families can see who's free
    before picking a preference — admin still makes the final assignment.

    If a family town is supplied, each sitter's real distance from that
    town is calculated and the list is sorted closest-first so families
    naturally see practical, local matches ahead of far-away ones.

    Safety gate: a sitter whose annual police clearance / Child Protection
    Register re-verification has lapsed (more than 12 months since it was
    last accepted) is left out of this list even if the old `verified` flag
    is still set to 1 in the database — families should never be shown a
    sitter as verified once their clearance documents are out of date."""
    family_location = geocode_place(town, province) if town else None
    rows = [dict(r) for r in db.execute(
        "SELECT * FROM babysitters WHERE verified = 1 ORDER BY rating DESC, created_at ASC"
    ).fetchall()]
    rows = [
        r for r in rows
        if compute_verification_status(r.get("verification_issued_date", ""), r.get("created_at", "")).get(
            "verification_status"
        ) != "overdue"
    ]
    window = None
    if date and start_time and duration_hours:
        try:
            window = booking_window(date, start_time, float(duration_hours))
        except Exception:
            window = None
    profiles = []
    for r in rows:
        available = None
        if date:
            unavailable_dates = set(d for d in (r.get("unavailable_dates") or "").split(",") if d)
            available = date not in unavailable_dates
            if available and window:
                clash = db.execute(
                    """SELECT booking_date, start_time, duration_hours FROM bookings
                    WHERE assigned_sitter_id = ? AND booking_date = ? AND status IN ('accepted','pending_match')""",
                    (r["id"], date),
                ).fetchall()
                for c in clash:
                    try:
                        other = booking_window(c["booking_date"], c["start_time"], c["duration_hours"])
                    except Exception:
                        continue
                    if window[0] < other[1] and other[0] < window[1]:
                        available = False
                        break
        distance_km = None
        if family_location and r.get("lat") is not None and r.get("lon") is not None:
            distance_km = round(haversine_km(family_location[0], family_location[1], r["lat"], r["lon"]), 1)
        profiles.append(sitter_public_profile(r, available, distance_km))
    if family_location:
        profiles.sort(key=lambda p: (p["distance_km"] is None, p["distance_km"] if p["distance_km"] is not None else 0))
    return {"babysitters": profiles, "local_radius_km": LOCAL_RADIUS_KM}


@app.get("/api/coverage-check")
def coverage_check(town: str, province: Optional[str] = None):
    """Public, no-signup way for a family to check — before filling in a
    full registration or booking — whether we currently have a verified
    babysitter within our 40km local service area of their town. Powers
    the "Check if we cover your area" box on the website."""
    location = geocode_place(town, province)
    if not location:
        return {
            "town": town, "resolved": False, "covered": None, "nearest_km": None,
            "local_radius_km": LOCAL_RADIUS_KM,
            "message": "We couldn't recognise that town — please check the spelling or try a nearby bigger town.",
        }
    nearest = nearest_sitter_distance(location[0], location[1])
    if nearest is None:
        return {
            "town": town, "resolved": True, "covered": False, "nearest_km": None,
            "local_radius_km": LOCAL_RADIUS_KM,
            "message": "We don't have any verified babysitters yet — check back soon as we onboard more sitters.",
        }
    covered = nearest["distance_km"] <= LOCAL_RADIUS_KM
    return {
        "town": town, "resolved": True, "covered": covered, "nearest_km": nearest["distance_km"],
        "local_radius_km": LOCAL_RADIUS_KM,
        "message": (
            f"Good news — we have a verified babysitter about {nearest['distance_km']}km from {town.strip()}."
            if covered else
            f"The closest verified babysitter we have is about {nearest['distance_km']}km away, which is "
            f"outside our {LOCAL_RADIUS_KM}km local service area. Contact us so we can look into finding a "
            "sitter closer to you."
        ),
    }


@app.get("/api/service-areas")
def service_areas():
    """Public list of towns where we currently have at least one verified,
    active babysitter — grows automatically as sitters register and finish
    verification. Powers the "Where we currently operate" list on the
    website, with no manual updates needed."""
    sitters = active_sitters_with_location()
    areas: dict = {}
    for s in sitters:
        key = (s.get("town") or "").strip()
        if not key:
            continue
        province = (s.get("province") or "").strip()
        entry = areas.setdefault(key, {"town": key, "province": province, "sitter_count": 0})
        entry["sitter_count"] += 1
    result = sorted(areas.values(), key=lambda a: (-a["sitter_count"], a["town"]))
    return {"areas": result, "local_radius_km": LOCAL_RADIUS_KM}


@app.get("/api/babysitters/{sitter_id}/photo")
def babysitter_public_photo(sitter_id: int):
    row = db.execute(
        "SELECT selfie_data, selfie_mimetype, verified FROM babysitters WHERE id = ?", (sitter_id,)
    ).fetchone()
    if not row or not row["verified"] or not row["selfie_data"]:
        raise HTTPException(404, "No profile photo available.")
    raw = base64.b64decode(row["selfie_data"])
    return Response(content=raw, media_type=row["selfie_mimetype"] or "image/jpeg")


@app.get("/api/admin/bookings")
def admin_list_bookings(admin_ok: bool = Depends(require_admin)):
    rows = [dict(r) for r in db.execute("SELECT * FROM bookings ORDER BY created_at DESC").fetchall()]
    sitters = {s["id"]: s for s in (dict(r) for r in db.execute(
        "SELECT id, full_name, email, phone, verified FROM babysitters"
    ).fetchall())}
    for r in rows:
        sid = r.get("assigned_sitter_id")
        r["assigned_sitter"] = sitters.get(sid) if sid else None
        psid = r.get("preferred_sitter_id")
        r["preferred_sitter"] = sitters.get(psid) if psid else None
        strip_document_blobs(r)
    return {"bookings": rows}


@app.get("/api/admin/bookings/{booking_id}/document/{document_type}")
def admin_get_booking_document(booking_id: int, document_type: str, admin_ok: bool = Depends(require_admin)):
    if document_type not in DOCUMENT_KINDS:
        raise HTTPException(400, "Unknown document type.")
    row = db.execute(
        f"SELECT {document_type}_data AS data, {document_type}_filename AS filename, "
        f"{document_type}_mimetype AS mimetype FROM bookings WHERE id = ?",
        (booking_id,),
    ).fetchone()
    if not row or not row["data"]:
        raise HTTPException(404, "This family hasn't uploaded this document yet.")
    raw = base64.b64decode(row["data"])
    filename = row["filename"] or document_type
    return Response(
        content=raw,
        media_type=row["mimetype"] or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


class AdminFamilyVerifyRequest(BaseModel):
    family_id_verified: bool = False
    family_proof_of_address_verified: bool = False
    registration_fee_paid: bool = False
    admin_notes: Optional[str] = ""


@app.post("/api/admin/bookings/{booking_id}/verify")
def admin_verify_family(booking_id: int, payload: AdminFamilyVerifyRequest, admin_ok: bool = Depends(require_admin)):
    row = db.execute(
        "SELECT id, registration_fee_paid, fee_paid_at FROM bookings WHERE id = ?", (booking_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, "Booking not found.")
    verified = payload.family_id_verified and payload.family_proof_of_address_verified
    # R99 is now an annual fee for families too, so stamp the date it was
    # confirmed paid — admin can see when a repeat family last paid and
    # judge whether a new booking falls inside the same 12-month window.
    was_paid = bool(row["registration_fee_paid"])
    if payload.registration_fee_paid and not was_paid:
        fee_paid_at = now_iso()[:10]
    elif payload.registration_fee_paid:
        fee_paid_at = row["fee_paid_at"] or now_iso()[:10]
    else:
        fee_paid_at = ""
    db.execute(
        """UPDATE bookings SET family_id_verified=?, family_proof_of_address_verified=?,
        registration_fee_paid=?, fee_paid_at=?, family_verified=?, admin_notes=? WHERE id=?""",
        (
            int(payload.family_id_verified), int(payload.family_proof_of_address_verified),
            int(payload.registration_fee_paid), fee_paid_at,
            int(verified), payload.admin_notes or "", booking_id,
        ),
    )
    db.commit()
    return {"id": booking_id, "family_verified": verified}


@app.post("/api/smile-id/callback")
async def smile_id_callback(request: Request):
    """Smile ID posts the final verification result here asynchronously
    (no auth header — Smile ID calls this directly). We store the raw
    result for admin review rather than auto-approving anyone, since a
    wrong auto-approval on a platform that serves families with children
    is a much bigger risk than an admin doing one extra manual check."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    partner_params = body.get("PartnerParams") or body.get("partner_params") or {}
    user_id = partner_params.get("user_id") or body.get("user_id") or ""
    result_text = body.get("ResultText") or body.get("result_text") or ""
    result_code = body.get("ResultCode") or body.get("result_code") or ""
    summary = f"{result_code}: {result_text}".strip(": ")
    if "-" not in user_id:
        return {"ok": False, "message": "unrecognised user_id in callback"}
    kind, _, rec_id = user_id.partition("-")
    table = "babysitters" if kind == "sitter" else "bookings" if kind == "family" else None
    if not table or not rec_id.isdigit():
        return {"ok": False, "message": "unrecognised user_id in callback"}
    db.execute(
        f"UPDATE {table} SET smile_id_api_status = 'received', smile_id_result_summary = ? WHERE id = ?",
        (summary, int(rec_id)),
    )
    db.commit()
    return {"ok": True}


class AdminAssignRequest(BaseModel):
    sitter_id: int


@app.post("/api/admin/bookings/{booking_id}/assign")
def admin_assign_sitter(booking_id: int, payload: AdminAssignRequest, admin_ok: bool = Depends(require_admin)):
    booking = db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not booking:
        raise HTTPException(404, "Booking not found.")
    booking = dict(booking)
    sitter = db.execute("SELECT * FROM babysitters WHERE id = ?", (payload.sitter_id,)).fetchone()
    if not sitter:
        raise HTTPException(404, "Sitter not found.")
    new_start, new_end = booking_window(booking["booking_date"], booking["start_time"], booking["duration_hours"])
    others = [dict(r) for r in db.execute(
        "SELECT * FROM bookings WHERE assigned_sitter_id = ? AND id != ? AND sitter_response != 'declined'",
        (payload.sitter_id, booking_id),
    ).fetchall()]
    clashes = []
    for o in others:
        o_start, o_end = booking_window(o["booking_date"], o["start_time"], o["duration_hours"])
        if new_start < o_end and new_end > o_start:
            clashes.append(o["booking_ref"])
    db.execute(
        "UPDATE bookings SET assigned_sitter_id = ?, sitter_response = 'pending', status = 'assigned' WHERE id = ?",
        (payload.sitter_id, booking_id),
    )
    db.commit()
    return {"id": booking_id, "assigned_sitter_id": payload.sitter_id, "clashes": clashes}


@app.post("/api/admin/bookings/{booking_id}/unassign")
def admin_unassign_sitter(booking_id: int, admin_ok: bool = Depends(require_admin)):
    row = db.execute("SELECT id FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Booking not found.")
    db.execute(
        "UPDATE bookings SET assigned_sitter_id = NULL, sitter_response = 'unassigned', status = 'pending_match' WHERE id = ?",
        (booking_id,),
    )
    db.commit()
    return {"id": booking_id}


class AdminManualBookingRequest(BaseModel):
    """For when admin needs to capture a booking directly — e.g. a phone-in
    request, or the family-facing system is temporarily unavailable. Skips
    the family's own document/selfie verification steps since admin is
    entering this by hand, but still records all the same scheduling, pet,
    and special-request details."""
    parent_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=20)
    email: Optional[str] = ""
    address: str = Field(min_length=5, max_length=300)
    children_count: str = Field(min_length=1, max_length=20)
    booking_date: str
    start_time: str
    rate_type: str
    level: str
    hourly_rate: float = Field(gt=0)
    duration_hours: float = Field(gt=0)
    special_instructions: Optional[str] = ""
    has_pets: bool = False
    pet_type: Optional[str] = ""
    special_bath_baby: bool = False
    special_feed_baby: bool = False
    special_precautions: Optional[str] = ""
    assign_sitter_id: Optional[int] = None
    admin_notes: Optional[str] = ""

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
            raise ValueError("rate_type must be 'day', 'overnight', or 'full_day'")
        return v


@app.post("/api/admin/bookings/manual", status_code=201)
def admin_create_manual_booking(payload: AdminManualBookingRequest, admin_ok: bool = Depends(require_admin)):
    quote = compute_rate_check(payload.level, payload.rate_type, payload.hourly_rate, payload.duration_hours)
    ref = gen_booking_ref()
    pin = gen_pin()
    assigned_id = None
    status = "pending_match"
    if payload.assign_sitter_id is not None:
        sitter = db.execute("SELECT id FROM babysitters WHERE id = ?", (payload.assign_sitter_id,)).fetchone()
        if not sitter:
            raise HTTPException(400, "Selected babysitter not found.")
        assigned_id = payload.assign_sitter_id
        status = "assigned"
    emailed = send_contract_email(payload.email, payload.parent_name, "family") if (payload.email or "").strip() else False
    cur = db.execute(
        """INSERT INTO bookings
        (booking_ref, pin, parent_name, id_number, phone, email, address, children_count,
         booking_date, start_time, rate_type, level, hourly_rate, duration_hours,
         special_instructions, status, agreed_terms, contract_sent, created_at,
         has_pets, pet_type, special_bath_baby, special_feed_baby, special_precautions,
         assigned_sitter_id, sitter_response, created_by_admin, admin_notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            ref, pin, payload.parent_name, "", payload.phone, payload.email or "", payload.address,
            payload.children_count, payload.booking_date, payload.start_time, payload.rate_type,
            payload.level, quote["applied_hourly_rate"], payload.duration_hours,
            payload.special_instructions, status, 1, int(emailed), now_iso(),
            int(payload.has_pets), payload.pet_type, int(payload.special_bath_baby),
            int(payload.special_feed_baby), payload.special_precautions,
            assigned_id, "pending" if assigned_id else "", 1, payload.admin_notes or "",
        ),
    )
    db.commit()
    return {
        "id": cur.lastrowid, "booking_ref": ref, "pin": pin, "status": status,
        "assigned_sitter_id": assigned_id, "quote": quote,
    }


# ---------------------------------------------------------------------------
# Sitter dashboard API — each sitter authenticates with their email + the
# access_code shown at registration (also included in their emailed
# contract confirmation).
# ---------------------------------------------------------------------------
class SitterAuthRequest(BaseModel):
    email: str
    access_code: str


@app.post("/api/sitter/login")
def sitter_login(payload: SitterAuthRequest):
    sitter = authenticate_sitter(payload.email, payload.access_code)
    return sitter_public(sitter)


@app.post("/api/sitter/bookings")
def sitter_bookings(payload: SitterAuthRequest):
    sitter = authenticate_sitter(payload.email, payload.access_code)
    rows = [dict(r) for r in db.execute(
        "SELECT * FROM bookings WHERE assigned_sitter_id = ? ORDER BY booking_date, start_time",
        (sitter["id"],),
    ).fetchall()]
    bookings = [{
        "id": r["id"], "booking_ref": r["booking_ref"], "parent_name": r["parent_name"],
        "phone": r["phone"], "address": r["address"], "children_count": r["children_count"],
        "booking_date": r["booking_date"], "start_time": r["start_time"], "rate_type": r["rate_type"],
        "level": r["level"], "hourly_rate": r["hourly_rate"], "duration_hours": r["duration_hours"],
        "special_instructions": r["special_instructions"], "status": r["status"],
        "sitter_response": r["sitter_response"],
    } for r in rows]
    return {"sitter": sitter_public(sitter), "bookings": bookings}


class SitterRespondRequest(BaseModel):
    email: str
    access_code: str
    response: str

    @field_validator("response")
    @classmethod
    def check_response(cls, v):
        if v not in {"accepted", "declined"}:
            raise ValueError("response must be 'accepted' or 'declined'")
        return v


@app.post("/api/sitter/bookings/{booking_id}/respond")
def sitter_respond(booking_id: int, payload: SitterRespondRequest):
    sitter = authenticate_sitter(payload.email, payload.access_code)
    row = db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    booking = dict(row) if row else None
    if not booking or booking.get("assigned_sitter_id") != sitter["id"]:
        raise HTTPException(404, "This booking is not assigned to you.")
    if payload.response == "accepted":
        db.execute("UPDATE bookings SET sitter_response='accepted', status='confirmed' WHERE id=?", (booking_id,))
    else:
        db.execute(
            "UPDATE bookings SET sitter_response='unassigned', status='pending_match', assigned_sitter_id=NULL WHERE id=?",
            (booking_id,),
        )
    db.commit()
    return {"id": booking_id, "response": payload.response}


class SitterAvailabilityRequest(BaseModel):
    email: str
    access_code: str
    date: str
    action: str

    @field_validator("action")
    @classmethod
    def check_action(cls, v):
        if v not in {"add", "remove"}:
            raise ValueError("action must be 'add' or 'remove'")
        return v


@app.post("/api/sitter/unavailability")
def sitter_unavailability(payload: SitterAvailabilityRequest):
    sitter = authenticate_sitter(payload.email, payload.access_code)
    dates = set(d for d in (sitter.get("unavailable_dates") or "").split(",") if d)
    if payload.action == "add":
        dates.add(payload.date)
    else:
        dates.discard(payload.date)
    new_val = ",".join(sorted(dates))
    db.execute("UPDATE babysitters SET unavailable_dates = ? WHERE id = ?", (new_val, sitter["id"]))
    db.commit()
    return {"unavailable_dates": sorted(dates)}


class SitterRenewVerificationRequest(BaseModel):
    email: str
    access_code: str
    police_clearance_data: str = Field(default="")
    police_clearance_filename: str = Field(default="")
    police_clearance_mimetype: str = Field(default="")
    child_protection_clearance_data: str = Field(default="")
    child_protection_clearance_filename: str = Field(default="")
    child_protection_clearance_mimetype: str = Field(default="")
    foreign_police_clearance_data: str = Field(default="")
    foreign_police_clearance_filename: str = Field(default="")
    foreign_police_clearance_mimetype: str = Field(default="")


@app.post("/api/sitter/renew-verification")
def sitter_renew_verification(payload: SitterRenewVerificationRequest):
    """Annual self-service renewal: a sitter uploads a fresh police
    clearance (+ Child Protection Register clearance, + foreign police
    clearance if they registered with a passport) once their 12-month
    verification window is up. Documents are stored and the sitter is put
    back into pending_verification (dropped from the public list) and the
    R99 fee is marked due again, exactly like a first-time registration —
    admin must review the new documents and confirm payment before setting
    a fresh verification_issued_date and re-verifying the sitter. This
    deliberately does NOT reset the 12-month clock itself, so a sitter
    can't self-certify their own renewal without an admin check."""
    sitter = authenticate_sitter(payload.email, payload.access_code)
    validate_document_fields(
        payload.police_clearance_data, payload.police_clearance_mimetype, payload.police_clearance_filename,
        "police clearance certificate",
    )
    validate_document_fields(
        payload.child_protection_clearance_data, payload.child_protection_clearance_mimetype,
        payload.child_protection_clearance_filename, "Child Protection Register (Part B) clearance letter",
    )
    if (sitter.get("id_type") or "sa_id") == "passport":
        validate_document_fields(
            payload.foreign_police_clearance_data, payload.foreign_police_clearance_mimetype,
            payload.foreign_police_clearance_filename, "foreign police clearance certificate",
        )
    db.execute(
        """UPDATE babysitters SET
        police_clearance_data=?, police_clearance_filename=?, police_clearance_mimetype=?,
        child_protection_clearance_data=?, child_protection_clearance_filename=?, child_protection_clearance_mimetype=?,
        foreign_police_clearance_data=?, foreign_police_clearance_filename=?, foreign_police_clearance_mimetype=?,
        registration_fee_paid=0, fee_paid_at='', verified=0, status='pending_verification'
        WHERE id=?""",
        (
            payload.police_clearance_data, payload.police_clearance_filename, payload.police_clearance_mimetype,
            payload.child_protection_clearance_data, payload.child_protection_clearance_filename,
            payload.child_protection_clearance_mimetype,
            payload.foreign_police_clearance_data, payload.foreign_police_clearance_filename,
            payload.foreign_police_clearance_mimetype,
            sitter["id"],
        ),
    )
    db.commit()
    updated = db.execute("SELECT * FROM babysitters WHERE id = ?", (sitter["id"],)).fetchone()
    return {
        "sitter": sitter_public(dict(updated)),
        "message": (
            "Your renewal documents were received. Please pay the R99 annual verification fee again via the "
            "Paystack link on your dashboard — our team will review your documents and payment and confirm your "
            "verified status."
        ),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
