from src.utils.hasher import hash_password
import hashlib


def test_hash_password():
    string = "jungle"
    hash_string = hashlib.sha256(
        string.encode("utf-8")
    ).hexdigest()

    assert hash_password(string) == hash_string
