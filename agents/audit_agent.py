from utils.storage import append_audit_log, current_timestamp


def log_event(agent_name, step, status, message, data=None):
    entry = {
        "timestamp": current_timestamp(),
        "agent": agent_name,
        "step": step,
        "status": status,
        "message": message,
        "data": data or {}
    }
    append_audit_log(entry)
    return entry