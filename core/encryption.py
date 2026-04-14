import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ---------- Key Derivation ------
def derive_key(secret: str, salt: bytes) -> bytes:
    """
    Derives a 256-bit AES key from a secret using PBKDF2-HMAC-SHA256.
    """
    return hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=secret.encode('utf-8'),
        salt=salt,
        iterations=600_000,
        dklen=32
    )


def encrypt_with_key(key: bytes, plaintext: str) -> dict:
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext.encode('utf-8'), None)
    return {
        "iv": iv.hex(),
        "ciphertext": ciphertext.hex()
    }


def decrypt_with_key(key: bytes, encrypted_data: dict) -> str:
    iv = bytes.fromhex(encrypted_data["iv"])
    ciphertext = bytes.fromhex(encrypted_data["ciphertext"])
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(iv, ciphertext, None)
        return plaintext.decode('utf-8')
    except Exception:
        raise ValueError("Decryption failed — wrong key or corrupted data.")


# ---------- Password-based encryption ----------

def encrypt(secret: str, plaintext: str) -> dict:
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(secret, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext.encode('utf-8'), None)
    return {
        "salt": salt.hex(),
        "iv": iv.hex(),
        "ciphertext": ciphertext.hex()
    }


def decrypt(secret: str, encrypted_data: dict) -> str:
    salt = bytes.fromhex(encrypted_data["salt"])
    iv = bytes.fromhex(encrypted_data["iv"])
    ciphertext = bytes.fromhex(encrypted_data["ciphertext"])
    key = derive_key(secret, salt)
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(iv, ciphertext, None)
        return plaintext.decode('utf-8')
    except Exception:
        raise ValueError("Decryption failed — wrong secret or corrupted data.")
