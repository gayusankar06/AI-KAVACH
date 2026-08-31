import hashlib
import os


def hash_password(password):
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + ":" + hashed.hex()


def verify_password(password, stored):
    salt_hex, hash_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return hashed.hex() == hash_hex