import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ---------- Key Derivation ----------

def derive_key(master_password: str, salt: bytes) -> bytes:
    """
    Derives a 256-bit AES key from the master password using PBKDF2-HMAC-SHA256.
    """
    key = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=master_password.encode('utf-8'),
        salt=salt,
        iterations=600_000,   # NIST recommended minimum (2023)
        dklen=32              # 256-bit key
    )
    return key


# ---------- Encryption ----------

def encrypt(master_password: str, plaintext: str) -> dict:
    """
    Encrypts plaintext using AES-256-GCM.

    Returns a dict with:
        - salt (hex)
        - iv   (hex)
        - ciphertext (hex)
    """
    salt = os.urandom(16)          # 128-bit random salt
    iv   = os.urandom(12)          # 96-bit IV (recommended for GCM)

    key  = derive_key(master_password, salt)
    aesgcm = AESGCM(key)

    ciphertext = aesgcm.encrypt(iv, plaintext.encode('utf-8'), None)

    return {
        "salt":       salt.hex(),
        "iv":         iv.hex(),
        "ciphertext": ciphertext.hex()
    }


# ---------- Decryption ----------

def decrypt(master_password: str, encrypted_data: dict) -> str:
    """
    Decrypts AES-256-GCM encrypted data.

    Args:
        master_password: the user's master password
        encrypted_data:  dict with keys salt, iv, ciphertext (all hex strings)

    Returns:
        Original plaintext string.

    Raises:
        ValueError: if the password is wrong or data is tampered.
    """
    salt       = bytes.fromhex(encrypted_data["salt"])
    iv         = bytes.fromhex(encrypted_data["iv"])
    ciphertext = bytes.fromhex(encrypted_data["ciphertext"])

    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(iv, ciphertext, None)
        return plaintext.decode('utf-8')
    except Exception:
        raise ValueError("Decryption failed — wrong password or corrupted data.")