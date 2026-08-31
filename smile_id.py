#!/usr/bin/env python3
"""smile_id.py — Smile ID v3 biometric KYC integration (Elite Traders Lounge).

Submits the selfie + liveness-burst photos captured on the registration and
booking forms to Smile ID's production Biometric KYC product for automatic
identity/facial-liveness verification, using the v3 REST API
(https://docs.usesmileid.com):

  1. POST /v3/token           -> short-lived JWT for the "biometric_kyc" product
  2. POST /v3/biometric_kyc   -> multipart submission (selfie + liveness frames)

Reads credentials from environment variables so the same code works locally
(sandbox) and in production (Render):

  SMILE_ID_API_KEY        required — production API key, added in Render's
                           environment variable settings (never committed).
  SMILE_ID_PARTNER_ID     optional — defaults to "8030" (Elite Traders
                           Lounge's Smile ID partner ID; not a secret).
  SMILE_ID_CALLBACK_URL   optional — where Smile ID POSTs the async result.
  SMILE_ID_BASE_URL       optional — override for sandbox/testing.

Every public function is best-effort and never raises: if the API key has
not been configured yet, or the request fails for any reason, a dict with
status "not_configured" / "error" is returned so registration/booking never
gets blocked by a Smile ID outage or missing credential.
"""
import json
import os
from datetime import datetime, timezone

import requests

SMILE_ID_BASE = os.environ.get("SMILE_ID_BASE_URL", "https://api.smileidentity.com").rstrip("/")
SMILE_ID_PARTNER_ID = os.environ.get("SMILE_ID_PARTNER_ID", "8030").strip()
SMILE_ID_CALLBACK_URL = os.environ.get(
    "SMILE_ID_CALLBACK_URL",
    "https://elite-traders-lounge-api.onrender.com/api/smile-id/callback",
).strip()
PRIVACY_POLICY_URL = os.environ.get(
    "SMILE_ID_PRIVACY_POLICY_URL",
    "https://elite-traders-lounge.vercel.app/policies.html#popia",
).strip()

_REQUEST_TIMEOUT = 30


def _api_key() -> str:
    return os.environ.get("SMILE_ID_API_KEY", "").strip()


def is_configured() -> bool:
    """True once the user has pasted a real SMILE_ID_API_KEY into the environment."""
    return bool(_api_key())


def _get_token(product: str = "biometric_kyc") -> str:
    # Smile ID's /v3/token endpoint requires multipart/form-data (a plain
    # application/x-www-form-urlencoded body returns 415 Unsupported Media
    # Type). Passing a `files=` dict forces `requests` to encode as multipart
    # even though there is no actual file to upload here.
    resp = requests.post(
        f"{SMILE_ID_BASE}/v3/token",
        headers={"smileid-partner-id": SMILE_ID_PARTNER_ID, "smileid-api-key": _api_key()},
        files={"product": (None, product)},
        timeout=_REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["token"]


def submit_biometric_kyc(
    *,
    user_id: str,
    job_id: str,
    full_name: str,
    email: str,
    phone: str,
    id_type: str,
    id_number: str,
    selfie_bytes: bytes,
    liveness_bytes_list: list,
) -> dict:
    """Submit one Biometric KYC job (selfie + liveness burst) to Smile ID.

    Returns a dict that always has a "status" key:
      "not_configured" — SMILE_ID_API_KEY hasn't been added to this
                          environment's variables yet; nothing was sent.
      "submitted"       — accepted by Smile ID; result arrives later via the
                          callback_url ("job_id" is included).
      "error"           — request failed; "message" has the reason. Never
                          raises, so callers can safely ignore failures.
    """
    if not is_configured():
        return {"status": "not_configured", "message": "Smile ID API key has not been added yet."}

    try:
        token = _get_token("biometric_kyc")
    except Exception as exc:  # noqa: BLE001 — best-effort by design
        return {"status": "error", "message": f"could not obtain a Smile ID token: {exc}"}

    given_names, _, last_name = (full_name or "").strip().partition(" ")
    if not last_name:
        last_name = given_names or "Unknown"
    if not given_names:
        given_names = last_name

    smile_id_type = "PASSPORT" if id_type == "passport" else "NATIONAL_ID"

    consent = {
        "granted": True,
        "granted_at": datetime.now(timezone.utc).isoformat(),
        "notice_language": "en",
        "notice_privacy_policy_url": PRIVACY_POLICY_URL,
    }
    user_details = {"given_names": given_names, "last_name": last_name}
    if email:
        user_details["email"] = email
    if phone:
        user_details["phone_number"] = phone

    files = [("selfie_image", ("selfie.jpg", selfie_bytes, "image/jpeg"))]
    for i, frame in enumerate(liveness_bytes_list or []):
        files.append(("liveness_images", (f"liveness_{i}.jpg", frame, "image/jpeg")))

    data = {
        "country": "ZA",
        "id_type": smile_id_type,
        "consent": json.dumps(consent),
        "user_details": json.dumps(user_details),
        "partner_params": json.dumps({"user_id": user_id, "job_id": job_id}),
        "callback_url": SMILE_ID_CALLBACK_URL,
    }
    if id_number:
        data["id_number"] = id_number

    try:
        resp = requests.post(
            f"{SMILE_ID_BASE}/v3/biometric_kyc",
            headers={"SmileID-Token": token, "SmileID-Partner-ID": SMILE_ID_PARTNER_ID},
            data=data,
            files=files,
            timeout=_REQUEST_TIMEOUT,
        )
        if resp.status_code not in (200, 202):
            return {"status": "error", "message": f"Smile ID returned {resp.status_code}: {resp.text[:300]}"}
        body = resp.json() if resp.content else {}
        return {
            "status": "submitted",
            "job_id": body.get("job_id") or job_id,
            "message": body.get("message", ""),
        }
    except Exception as exc:  # noqa: BLE001 — best-effort by design
        return {"status": "error", "message": str(exc)}
