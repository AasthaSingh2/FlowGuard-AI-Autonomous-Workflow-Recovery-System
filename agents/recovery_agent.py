from agents.audit_agent import log_event


def recovery_agent(data: dict, failure_info: dict):
    if not failure_info.get("failure_detected"):
        return data

    missing_fields = failure_info.get("details", {}).get("missing_fields", [])

    recovered_data = data.copy()

    if "employee_id" in missing_fields:
        recovered_data["employee_id"] = "FG-AUTO-1001"

    recovery_result = {
        "recovered": True,
        "recovery_action": "Auto-generated missing employee ID",
        "updated_data": recovered_data
    }

    log_event(
        agent_name="Recovery Agent",
        step="recovery",
        status="success",
        message="Recovery action executed successfully",
        data=recovery_result
    )

    return recovered_data