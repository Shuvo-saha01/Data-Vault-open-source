import json
import os
from core.encryption import encrypt, decrypt

ENV_FILE = "data/env_vault.json"


def _load_env_vault() -> dict:
    if not os.path.exists(ENV_FILE):
        return {}
    with open(ENV_FILE, 'r') as f:
        return json.load(f)


def _save_env_vault(vault: dict):
    os.makedirs("data", exist_ok=True)
    with open(ENV_FILE, 'w') as f:
        json.dump(vault, f, indent=4)


def save_env(master_password: str, key: str, value: str):
    """
    Encrypts and saves an ENV variable.
    Example: save_env("master123", "DATABASE_URL", "postgres://...")
    """
    vault = _load_env_vault()
    vault[key] = encrypt(master_password, value)
    _save_env_vault(vault)
    print(f"ENV '{key}' saved successfully!")


def get_env(master_password: str, key: str) -> str:
    """
    Retrieves and decrypts an ENV variable.
    """
    vault = _load_env_vault()
    if key not in vault:
        raise KeyError(f"No ENV variable found for '{key}'")
    return decrypt(master_password, vault[key])


def list_env_keys() -> list:
    """
    Returns all saved ENV variable keys.
    """
    vault = _load_env_vault()
    return list(vault.keys())


def delete_env(key: str):
    """
    Deletes a saved ENV variable.
    """
    vault = _load_env_vault()
    if key not in vault:
        raise KeyError(f"No ENV variable found for '{key}'")
    del vault[key]
    _save_env_vault(vault)
    print(f"ENV '{key}' deleted!")


def export_env_file(master_password: str, output_path: str = ".env"):
    """
    Decrypts all ENV variables and exports them as a .env file.
    Example output:
        DATABASE_URL=postgres://...
        SECRET_KEY=abc123...
    """
    vault = _load_env_vault()
    if not vault:
        print("No ENV variables saved yet!")
        return

    with open(output_path, 'w') as f:
        for key, encrypted_value in vault.items():
            value = decrypt(master_password, encrypted_value)
            f.write(f"{key}={value}\n")

    print(f".env file exported to '{output_path}'!")