import json
import os
import shutil
from datetime import datetime
from core.encryption import encrypt, decrypt

VAULT_FILE = "data/vault.json"
ENV_VAULT_FILE = "data/env_vault.json"
BACKUP_DIR = "data/backups"


def create_backup(master_password: str) -> str:
    """
    Creates an encrypted backup of the entire vault.
    Returns the backup file path.
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Load both vaults
    vault_data = {}
    env_data = {}

    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, 'r') as f:
            vault_data = json.load(f)

    if os.path.exists(ENV_VAULT_FILE):
        with open(ENV_VAULT_FILE, 'r') as f:
            env_data = json.load(f)

    # Combine into one backup object
    backup_data = {
        "vault": vault_data,
        "env_vault": env_data,
        "created_at": datetime.now().isoformat()
    }

    # Encrypt the entire backup
    encrypted_backup = encrypt(master_password, json.dumps(backup_data))

    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}/backup_{timestamp}.vaultbackup"

    with open(backup_path, 'w') as f:
        json.dump(encrypted_backup, f, indent=4)

    print(f"Backup created: {backup_path}")
    return backup_path


def restore_backup(master_password: str, backup_path: str):
    """
    Restores vault from an encrypted backup file.
    """
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    with open(backup_path, 'r') as f:
        encrypted_backup = json.load(f)

    # Decrypt the backup
    try:
        decrypted = decrypt(master_password, encrypted_backup)
    except ValueError:
        raise ValueError("Wrong master password or corrupted backup!")

    backup_data = json.loads(decrypted)

    # Restore both vaults
    os.makedirs("data", exist_ok=True)

    with open(VAULT_FILE, 'w') as f:
        json.dump(backup_data["vault"], f, indent=4)

    with open(ENV_VAULT_FILE, 'w') as f:
        json.dump(backup_data["env_vault"], f, indent=4)

    print(f"Vault restored from: {backup_path}")
    print(f"Backup created at: {backup_data['created_at']}")


def list_backups() -> list:
    """
    Returns list of all available backup files.
    """
    if not os.path.exists(BACKUP_DIR):
        return []
    return [f for f in os.listdir(BACKUP_DIR) if f.endswith('.vaultbackup')]