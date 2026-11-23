"""Unit tests for GitHub Webhook HMAC-SHA256 signature verification."""

import hashlib
import hmac
import pytest
from backend.app.services.github.webhook_verifier import verify_signature


def test_verify_signature_valid():
    secret = "test_webhook_secret_key_123"
    payload = b'{"action": "opened", "number": 42}'
    expected_hex = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    header = f"sha256={expected_hex}"

    assert verify_signature(payload, header, secret) is True


def test_verify_signature_invalid_hash():
    secret = "test_webhook_secret_key_123"
    payload = b'{"action": "opened", "number": 42}'
    tampered_header = "sha256=0000000000000000000000000000000000000000000000000000000000000000"

    assert verify_signature(payload, tampered_header, secret) is False


def test_verify_signature_wrong_secret():
    secret1 = "secret_one"
    secret2 = "secret_two"
    payload = b'{"action": "opened"}'
    expected_hex = hmac.new(secret1.encode(), payload, hashlib.sha256).hexdigest()
    header = f"sha256={expected_hex}"

    assert verify_signature(payload, header, secret2) is False


def test_verify_signature_missing_header():
    assert verify_signature(b"payload", None, "secret") is False
    assert verify_signature(b"payload", "", "secret") is False


def test_verify_signature_malformed_header():
    assert verify_signature(b"payload", "invalid_prefix_without_sha256", "secret") is False

