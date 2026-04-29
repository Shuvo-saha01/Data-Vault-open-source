import json
import os
from core.encryption import encrypt, decrypt
from core.auth import login, register

AUTH_FILE = "data/auth.json"
STORAGE_FILE = "data/vault.json"
ENV_FILE = "data/env_vault.json"


def change_master_password(old_password: str, new_password: str):
    """
    Changes master password and re-encrypts ALL vault data.
    
    Steps:
    1. Verify old password
    2. Decrypt everything with old password
    3. Re-encrypt everything with new password
    4. Update stored password hash
    """

    # Step 1 - Verify old password
    if not login(old_password):
        raise ValueError("Wrong current password!")

    print("Old password verified...")

    # Step 2 - Re-encrypt password vault
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            vault = json.load(f)

        new_vault = {}
        for label, encrypted_value in vault.items():
            plaintext = decrypt(old_password, encrypted_value)
            new_vault[label] = encrypt(new_password, plaintext)

        with open(STORAGE_FILE, 'w') as f:
            json.dump(new_vault, f, indent=4)

        print(f"Re-encrypted {len(new_vault)} passwords...")

    # Step 3 - Re-encrypt ENV vault
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            env_vault = json.load(f)

        new_env_vault = {}
        for key, encrypted_value in env_vault.items():
            plaintext = decrypt(old_password, encrypted_value)
            new_env_vault[key] = encrypt(new_password, plaintext)

        with open(ENV_FILE, 'w') as f:
            json.dump(new_env_vault, f, indent=4)

        print(f"Re-encrypted {len(new_env_vault)} ENV variables...")

    # Step 4 - Update auth with new password hash
    os.remove(AUTH_FILE)
    register(new_password)

    print("Master password changed successfully!")
    print("Make sure to create a new backup!")