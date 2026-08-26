"""Normalize M-Pesa BillRefNumber / Client.account_number for lookup.

Policy: strip whitespace. Lookup tries the raw value first, then a form
with leading zeros removed (so 0001001 matches account 1001).
"""


def normalize_account_reference(value):
    if value is None:
        return ""
    compact = "".join(str(value).split())
    if not compact:
        return ""
    stripped = compact.lstrip("0")
    return stripped if stripped else "0"
