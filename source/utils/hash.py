import hashlib

def hash_password(password, hash_salt):
    """使用SHA-256加密密碼，並加上HASH_SALT"""
    salted = hash_salt + password
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()