import json
import os
from core.encryption import encrypt, decrypt

STORAGE_FILE = "data/vault.json"

def _load_vault() -> dict:
    if not os.path.exists(STORAGE_FILE):
        return {}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def _save_vault(vault: dict):
    os.makedirs("data", exist_ok=True)
    with open(STORAGE_FILE, 'w') as f:
        json.dump(vault, f, indent=4)

def save_password(master_password: str, label: str, password: str):
    vault = _load_vault()
    vault[label] = encrypt(master_password, password)
    _save_vault(vault)
    print(f"Password for '{label}' saved successfully!")

def get_password(master_password: str, label: str) -> str:
    vault = _load_vault()
    if label not in vault:
        raise KeyError(f"No password found for '{label}'")
    return decrypt(master_password, vault[label])

def list_labels() -> list:
    vault = _load_vault()
    return list(vault.keys())

def delete_password(label: str):
    vault = _load_vault()
    if label not in vault:
        raise KeyError(f"No password found for '{label}'")
    del vault[label]
    _save_vault(vault)
    print(f"Password for '{label}' deleted!")