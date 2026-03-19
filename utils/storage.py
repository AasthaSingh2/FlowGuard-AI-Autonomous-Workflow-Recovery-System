import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.json")
STATE_FILE = os.path.join(DATA_DIR, "workflow_state.json")


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)


def read_json(file_path, default):
    ensure_data_files()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(file_path, data):
    ensure_data_files()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def append_audit_log(entry):
    logs = read_json(AUDIT_FILE, [])
    logs.append(entry)
    write_json(AUDIT_FILE, logs)


def get_audit_logs():
    return read_json(AUDIT_FILE, [])


def clear_audit_logs():
    write_json(AUDIT_FILE, [])


def save_workflow_state(state):
    write_json(STATE_FILE, state)


def get_workflow_state():
    return read_json(STATE_FILE, {})


def current_timestamp():
    return datetime.now().isoformat()