import logging
import time
from base64 import b64encode

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

_token_cache = {"access_token": None, "expires_at": 0}


def mpesa_base_url():
    env = getattr(settings, "MPESA_ENV", "sandbox") or "sandbox"
    if env.lower() == "production":
        return "https://api.safaricom.co.ke"
    return "https://sandbox.safaricom.co.ke"


def _basic_auth_header():
    key = settings.MPESA_CONSUMER_KEY
    secret = settings.MPESA_CONSUMER_SECRET
    token = b64encode(f"{key}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def get_access_token(force_refresh=False):
    now = time.time()
    if (
        not force_refresh
        and _token_cache["access_token"]
        and _token_cache["expires_at"] > now + 60
    ):
        return _token_cache["access_token"]

    url = f"{mpesa_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, headers=_basic_auth_header(), timeout=30)
    response.raise_for_status()
    data = response.json()
    access_token = data["access_token"]
    expires_in = int(data.get("expires_in", 3600))
    _token_cache["access_token"] = access_token
    _token_cache["expires_at"] = now + expires_in
    return access_token


def _auth_headers():
    return {"Authorization": f"Bearer {get_access_token()}", "Content-Type": "application/json"}


def register_c2b_urls():
    base = (settings.MPESA_CALLBACK_BASE_URL or "").rstrip("/")
    secret = settings.MPESA_CALLBACK_SECRET
    if secret:
        validation = f"{base}/payments/mpesa/{secret}/validation/"
        confirmation = f"{base}/payments/mpesa/{secret}/confirmation/"
    else:
        validation = f"{base}/payments/mpesa/validation/"
        confirmation = f"{base}/payments/mpesa/confirmation/"

    payload = {
        "ShortCode": settings.MPESA_SHORTCODE,
        "ResponseType": "Completed",
        "ConfirmationURL": confirmation,
        "ValidationURL": validation,
    }
    url = f"{mpesa_base_url()}/mpesa/c2b/v1/registerurl"
    response = requests.post(url, json=payload, headers=_auth_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def simulate_c2b(amount, bill_ref_number, msisdn="254708374149"):
    """Simulate C2B payment. In sandbox, use shortcode 174379 and test phone 254708374149."""
    payload = {
        "ShortCode": settings.MPESA_SHORTCODE,
        "CommandID": "CustomerPayBillOnline",
        "Amount": str(amount),
        "Msisdn": msisdn,
        "BillRefNumber": str(bill_ref_number),
    }
    url = f"{mpesa_base_url()}/mpesa/c2b/v1/simulate"
    response = requests.post(url, json=payload, headers=_auth_headers(), timeout=30)
    response.raise_for_status()
    return response.json()
