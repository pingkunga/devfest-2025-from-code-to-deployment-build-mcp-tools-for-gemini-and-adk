# app/utils/line_sig.py
import base64
import hashlib
import hmac


def verify_line_signature(secret: str, body: bytes, signature_b64: str) -> bool:
    mac = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    expected = base64.b64encode(mac).decode("utf-8")
    return hmac.compare_digest(expected, signature_b64 or "")
