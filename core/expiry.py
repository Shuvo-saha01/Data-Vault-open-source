import json
import os
from datetime import datetime, timedelta

METADATA_FILE = "data/pwd_metadata.json"

def _load_metadata() -> dict:
    if not os.path.exists(METADATA_FILE):
        return {}
    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

def _save_metadata(meta: dict):
    os.makedirs("data", exist_ok=True)
    with open(METADATA_FILE, 'w') as f:
        json.dump(meta, f, indent=4)

def update_password_date(label: str):
    """Records the date a password was saved or updated."""
    meta = _load_metadata()
    meta[label] = datetime.now().isoformat()
    _save_metadata(meta)

def get_expired_passwords(days_limit: int = 90) -> list:
    """Returns a list of labels that are older than days_limit."""
    meta = _load_metadata()
    expired = []
    now = datetime.now()

    for label, date_str in meta.items():
        try:
            saved_date = datetime.fromisoformat(date_str)
            if now - saved_date > timedelta(days=days_limit):
                expired.append(label)
        except ValueError:
            continue
            
    return expired