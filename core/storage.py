import json
import os

DATA_VAULT = "vault.json"

DEFAULT_VAULT = {
    "auth": None,
    "recovery": None,
    "encrypted_key_master": None,
    "encrypted_key_recovery": None,
    "passwords": []
}


def load_vault():
    if not os.path.exists(DATA_VAULT):
        return DEFAULT_VAULT.copy()

    with open(DATA_VAULT, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return DEFAULT_VAULT.copy()

    if isinstance(data, list):
        return {
            "auth": None,
            "recovery": None,
            "encrypted_key_master": None,
            "encrypted_key_recovery": None,
            "passwords": data
        }

    result = DEFAULT_VAULT.copy()
    result.update(data)
    result.setdefault("passwords", [])
    return result


def save_vault(data):
    with open(DATA_VAULT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
