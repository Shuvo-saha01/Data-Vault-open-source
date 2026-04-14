import hashlib
import os
from cryptography.hazmat.primitives import constant_time
from core.encryption import encrypt, decrypt

HASH_ITERATIONS = 600_000
KEY_LEN = 32


def normalize_text(value: str) -> str:
    return value.strip().lower()


def hash_master_password(password: str) -> dict:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
        dklen=KEY_LEN
    )
    return {
        "salt": salt.hex(),
        "hash": digest.hex(),
        "iterations": HASH_ITERATIONS
    }


def verify_master_password(password: str, auth_data: dict) -> bool:
    salt = bytes.fromhex(auth_data["salt"])
    expected = bytes.fromhex(auth_data["hash"])
    test = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        auth_data.get("iterations", HASH_ITERATIONS),
        dklen=KEY_LEN
    )
    return constant_time.bytes_eq(test, expected)


def build_recovery_secret(mode: str, answers: list) -> str:
    if mode == "text":
        return "|".join(normalize_text(answer) for answer in answers)
    return "|".join(str(answer) for answer in answers)


def verify_recovery_answers(recovery_data: dict, answers: list) -> bool:
    if recovery_data is None:
        return False
    if recovery_data["mode"] == "text":
        expected = [normalize_text(value) for value in recovery_data["answers"]]
        return [normalize_text(value) for value in answers] == expected
    return [int(value) for value in answers] == recovery_data.get("correct", [])


def derive_recovery_secret(recovery_data: dict, answers: list) -> str:
    return build_recovery_secret(recovery_data["mode"], answers)


def encrypt_vault_key(master_secret: str, vault_key_hex: str) -> dict:
    return encrypt(master_secret, vault_key_hex)


def decrypt_vault_key(master_secret: str, encrypted_key: dict) -> str:
    return decrypt(master_secret, encrypted_key)
