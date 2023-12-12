"""
This module contains a function that hashes a string using
the SHA-256 algorithm.
"""

import hashlib


def hash_password(string) -> str:
    """
    Hashes password string using the SHA-256 algorithm.

    Args:
    - string (str): The string to be hashed.

    Returns:
    - str: The hashed string using the SHA-256 algorithm.

    This function takes a string as input, encodes it to UTF-8,
    and then hashes it using the SHA-256 algorithm from the hashlib library.
    The resulting hashed string is returned.
    """
    return hashlib.sha256(string.encode('utf-8')).hexdigest()
