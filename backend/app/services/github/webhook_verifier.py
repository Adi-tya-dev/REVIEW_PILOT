"""GitHub Webhook HMAC-SHA256 signature verification."""

import hashlib
import hmac
from typing import Optional


def verify_signature(payload_bytes: bytes, signature_header: Optional[str], secret: str) -> bool:
    """Verify that the webhook signature matches the payload and secret.

    Args:
        payload_bytes: Raw HTTP request body bytes.
        signature_header: Content of the 'X-Hub-Signature-256' header (e.g. 'sha256=abcdef...').
        secret: Configured webhook secret.

    Returns:
        True if valid, False otherwise.
    """
    if not signature_header or not secret:
        return False

    if not signature_header.startswith("sha256="):
        return False

    received_sig = signature_header.split("sha256=", 1)[1].strip()

    expected_sig = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to protect against timing attacks
    return hmac.compare_digest(expected_sig, received_sig)

