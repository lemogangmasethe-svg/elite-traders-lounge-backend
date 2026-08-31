#!/usr/bin/env python3
"""api_server.py — Elite Traders Lounge backend.

Handles babysitter registration, parent/guardian registration + booking
requests, and the dual (babysitter + parent/guardian) arrival/departure
confirmation system used to track worked hours for every booking.

Runs on port 8000 inside the sandbox.
"""
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

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator, model_validator

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
]


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

        def __init__(self, conn):
            self._conn = conn

        def execute(self, sql, params=()):
            pg_sql = sql.replace("?", "%s")
            needs_id = pg_sql.strip().upper().startswith(
                ("INSERT INTO BABYSITTERS", "INSERT INTO BOOKINGS")
            ) and "RETURNING" not in pg_sql.upper()
            if needs_id:
                pg_sql += " RETURNING id"
            cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(pg_sql, params)
            lastrowid = None
            if needs_id:
                row = cur.fetchone()
                lastrowid = row["id"] if row else None
            return _PgCursor(cur, lastrowid=lastrowid)

        def executescript(self, script):
            # Schema is provisioned separately (via migration) in Postgres.
            pass

        def commit(self):
            self._conn.commit()

        def close(self):
            self._conn.close()

    def get_db():
        conn = psycopg2.connect(DATABASE_URL)
        return _PgConn(conn)

else:
    def get_db():
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn


db = get_db()
if not USE_POSTGRES:
    db.executescript(SCHEMA_SQL)
    db.commit()
run_migrations(db)


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
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "status": row["status"],
        "verified": bool(row["verified"]),
        "experience_level": row["experience_level"],
        "unavailable_dates": sorted(d for d in (row.get("unavailable_dates") or "").split(",") if d),
    }


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
    id_type: str = "sa_id"
    id_number: Optional[str] = Field(default="", max_length=20)
    passport_number: Optional[str] = ""
    nationality: Optional[str] = ""
    work_permit_number: Optional[str] = ""
    work_permit_expiry: Optional[str] = ""
    phone: str = Field(min_length=7, max_length=20)
    email: str
    address: str = Field(min_length=5, max_length=300)
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
    paystack_email: str
    smile_id_consent: bool
    bank_name: Optional[str] = ""
    account_holder: Optional[str] = ""
    account_number: Optional[str] = ""
    agreed_terms: bool

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
        if self.id_type == "passport":
            missing = [
                name for name in ("passport_number", "nationality", "work_permit_number", "work_permit_expiry")
                if not (getattr(self, name) or "").strip()
            ]
            if missing:
                raise ValueError(
                    "passport, nationality, and a valid work permit number + expiry date are required for "
                    "non-South African freelance babysitters to stay compliant with SA immigration law"
                )
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


class BookingRequest(BaseModel):
    parent_name: str = Field(min_length=2, max_length=120)
    id_type: str = "sa_id"
    id_number: Optional[str] = Field(default="", max_length=20)
    passport_number: Optional[str] = ""
    nationality: Optional[str] = ""
    phone: str = Field(min_length=7, max_length=20)
    email: str
    address: str = Field(min_length=5, max_length=300)
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
    agreed_terms: bool

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


@app.post("/api/register-sitter", status_code=201)
def register_sitter(payload: SitterRegistration):
    emailed = send_contract_email(payload.email, payload.full_name, "sitter")
    access_code = gen_access_code()
    cur = db.execute(
        """INSERT INTO babysitters
        (full_name, id_type, id_number, passport_number, nationality, work_permit_number,
         work_permit_expiry, phone, email, address, proof_of_address_type,
         proof_of_address_confirmed, experience_level, years_experience, certifications,
         references_text, availability, reference_name, reference_relationship,
         reference_phone, reference_email, reference_affidavit_consent, paystack_email,
         smile_id_consent, bank_name, account_holder, account_number, agreed_terms,
         contract_sent, access_code, status, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            payload.full_name, payload.id_type, payload.id_number, payload.passport_number,
            payload.nationality, payload.work_permit_number, payload.work_permit_expiry,
            payload.phone, payload.email, payload.address, payload.proof_of_address_type,
            int(payload.proof_of_address_confirmed), payload.experience_level,
            payload.years_experience, payload.certifications,
            f"{payload.reference_name} ({payload.reference_relationship}) — {payload.reference_phone}, {payload.reference_email}",
            payload.availability, payload.reference_name, payload.reference_relationship,
            payload.reference_phone, payload.reference_email, int(payload.reference_affidavit_consent),
            payload.paystack_email, int(payload.smile_id_consent), payload.bank_name,
            payload.account_holder, payload.account_number, int(payload.agreed_terms),
            int(emailed), access_code, "pending_verification", now_iso(),
        ),
    )
    db.commit()
    return {
        "id": cur.lastrowid,
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
    emailed = send_contract_email(payload.email, payload.parent_name, "family")
    db.execute(
        """INSERT INTO bookings
        (booking_ref, pin, parent_name, id_type, id_number, passport_number, nationality,
         phone, email, address, proof_of_address_type, proof_of_address_confirmed,
         children_count, paystack_email, smile_id_consent, booking_date, start_time,
         rate_type, level, hourly_rate, duration_hours, special_instructions, status,
         agreed_terms, contract_sent, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            ref, pin, payload.parent_name, payload.id_type, payload.id_number,
            payload.passport_number, payload.nationality, payload.phone, payload.email,
            payload.address, payload.proof_of_address_type, int(payload.proof_of_address_confirmed),
            payload.children_count, payload.paystack_email, int(payload.smile_id_consent),
            payload.booking_date, payload.start_time, payload.rate_type, payload.level,
            quote["applied_hourly_rate"], payload.duration_hours, payload.special_instructions,
            "pending_match", int(payload.agreed_terms), int(emailed), now_iso(),
        ),
    )
    db.commit()
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


@app.get("/api/admin/sitters")
def admin_list_sitters(admin_ok: bool = Depends(require_admin)):
    rows = [dict(r) for r in db.execute("SELECT * FROM babysitters ORDER BY created_at DESC").fetchall()]
    return {"sitters": rows}


class AdminSitterVerifyRequest(BaseModel):
    id_doc_verified: bool = False
    proof_of_address_verified: bool = False
    reference_verified: bool = False
    smile_id_verified: bool = False
    admin_notes: Optional[str] = ""


@app.post("/api/admin/sitters/{sitter_id}/verify")
def admin_verify_sitter(sitter_id: int, payload: AdminSitterVerifyRequest, admin_ok: bool = Depends(require_admin)):
    row = db.execute("SELECT id FROM babysitters WHERE id = ?", (sitter_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Sitter not found.")
    verified = (
        payload.id_doc_verified and payload.proof_of_address_verified
        and payload.reference_verified and payload.smile_id_verified
    )
    status = "verified" if verified else "pending_verification"
    db.execute(
        """UPDATE babysitters SET id_doc_verified=?, proof_of_address_verified=?, reference_verified=?,
        smile_id_verified=?, verified=?, status=?, admin_notes=? WHERE id=?""",
        (
            int(payload.id_doc_verified), int(payload.proof_of_address_verified),
            int(payload.reference_verified), int(payload.smile_id_verified),
            int(verified), status, payload.admin_notes or "", sitter_id,
        ),
    )
    db.commit()
    return {"id": sitter_id, "verified": verified, "status": status}


@app.get("/api/admin/bookings")
def admin_list_bookings(admin_ok: bool = Depends(require_admin)):
    rows = [dict(r) for r in db.execute("SELECT * FROM bookings ORDER BY created_at DESC").fetchall()]
    sitters = {s["id"]: s for s in (dict(r) for r in db.execute(
        "SELECT id, full_name, email, phone, verified FROM babysitters"
    ).fetchall())}
    for r in rows:
        sid = r.get("assigned_sitter_id")
        r["assigned_sitter"] = sitters.get(sid) if sid else None
    return {"bookings": rows}


class AdminFamilyVerifyRequest(BaseModel):
    family_id_verified: bool = False
    family_proof_of_address_verified: bool = False
    admin_notes: Optional[str] = ""


@app.post("/api/admin/bookings/{booking_id}/verify")
def admin_verify_family(booking_id: int, payload: AdminFamilyVerifyRequest, admin_ok: bool = Depends(require_admin)):
    row = db.execute("SELECT id FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Booking not found.")
    verified = payload.family_id_verified and payload.family_proof_of_address_verified
    db.execute(
        """UPDATE bookings SET family_id_verified=?, family_proof_of_address_verified=?,
        family_verified=?, admin_notes=? WHERE id=?""",
        (
            int(payload.family_id_verified), int(payload.family_proof_of_address_verified),
            int(verified), payload.admin_notes or "", booking_id,
        ),
    )
    db.commit()
    return {"id": booking_id, "family_verified": verified}


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
