import hashlib


def hash_password(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()
