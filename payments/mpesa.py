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
    shortcode = getattr(settings, "MPESA_SHORTCODE", "") or "174379"
    payload = {
        "ShortCode": shortcode,
        "CommandID": "CustomerPayBillOnline",
        "Amount": str(amount),
        "Msisdn": msisdn,
        "BillRefNumber": str(bill_ref_number),
    }
    url = f"{mpesa_base_url()}/mpesa/c2b/v1/simulate"
    response = requests.post(url, json=payload, headers=_auth_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def format_phone_number(phone):
    """Format phone number to Safaricom 254XXXXXXXXX format."""
    if not phone:
        return ""
    digits = "".join(c for c in str(phone) if c.isdigit())
    if digits.startswith("0") and len(digits) == 10:
        return "254" + digits[1:]
    elif digits.startswith("254") and len(digits) == 12:
        return digits
    elif len(digits) == 9 and (digits.startswith("7") or digits.startswith("1")):
        return "254" + digits
    return digits


def initiate_stk_push(phone_number, amount, account_reference, transaction_desc="Water Bill Payment", callback_url=None):
    """
    Send M-Pesa Express (STK Push) prompt via Safaricom Daraja API.
    """
    formatted_phone = format_phone_number(phone_number)
    if not formatted_phone or len(formatted_phone) != 12:
        raise ValueError("Invalid phone number format. Must be in format 254XXXXXXXXX or 07XXXXXXXX.")

    shortcode = (getattr(settings, "MPESA_SHORTCODE", "") or "174379").strip()
    passkey = (getattr(settings, "MPESA_PASSKEY", "") or "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919").strip()

    timestamp = time.strftime("%Y%m%d%H%M%S")
    password_str = f"{shortcode}{passkey}{timestamp}"
    password = b64encode(password_str.encode()).decode()

    if not callback_url:
        base = (getattr(settings, "MPESA_CALLBACK_BASE_URL", "") or "https://waterbilling-r92q.onrender.com").rstrip("/")
        secret = getattr(settings, "MPESA_CALLBACK_SECRET", "")
        if secret:
            callback_url = f"{base}/payments/mpesa/stkpush/{secret}/callback/"
        else:
            callback_url = f"{base}/payments/mpesa/stkpush/callback/"

    # Round amount to whole integer or 2 decimals
    amt_val = max(1, int(round(float(amount))))

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": str(amt_val),
        "PartyA": formatted_phone,
        "PartyB": shortcode,
        "PhoneNumber": formatted_phone,
        "CallBackURL": callback_url,
        "AccountReference": str(account_reference)[:12],
        "TransactionDesc": str(transaction_desc)[:12]
    }

    url = f"{mpesa_base_url()}/mpesa/stkpush/v1/processrequest"
    logger.info("Initiating M-Pesa STK Push to %s for KES %s (Ref: %s)", formatted_phone, amt_val, account_reference)

    response = requests.post(url, json=payload, headers=_auth_headers(), timeout=30)
    response.raise_for_status()
    return response.json()

