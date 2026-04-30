import bcrypt
import json
import os

AUTH_FILE = "data/auth.json"

def register(master_password: str) -> bool:
    """
    Hashes and saves the master password.
    Returns False if user already exists.
    """
    if os.path.exists(AUTH_FILE):
        print("User already registered!")
        return False

    os.makedirs("data", exist_ok=True)

    hashed = bcrypt.hashpw(
        master_password.encode('utf-8'),
        bcrypt.gensalt(rounds=12)
    )

    with open(AUTH_FILE, 'w') as f:
        json.dump({"password_hash": hashed.decode('utf-8')}, f)

    print("Master password set successfully!")
    return True


def login(master_password: str) -> bool:
    """
    Verifies master password against stored hash.
    Returns True if correct, False if wrong.
    """
    if not os.path.exists(AUTH_FILE):
        print("No user registered yet!")
        return False

    with open(AUTH_FILE, 'r') as f:
        data = json.load(f)

    stored_hash = data["password_hash"].encode('utf-8')

    return bcrypt.checkpw(
        master_password.encode('utf-8'),
        stored_hash
    )
