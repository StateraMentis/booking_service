from app.core.security import (
    get_password_hash,
    verify_password,
    verify_token,
)


def test_password_hash_and_verify():
    raw_password = "StrongPass123"
    hashed = get_password_hash(raw_password)

    assert hashed != raw_password
    assert verify_password(raw_password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_verify_token_returns_none_for_invalid_token():
    assert verify_token("not-a-real-token") is None
