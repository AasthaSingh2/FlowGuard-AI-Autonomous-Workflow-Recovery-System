from agents.audit_agent import log_event


def verification_agent(data: dict):
    missing_fields = []

    required_fields = ["candidate_name", "email", "employee_id"]

    for field in required_fields:
        if not data.get(field):
            missing_fields.append(field)

    if missing_fields:
        result = {
            "status": "failed",
            "reason": "Missing required fields",
            "missing_fields": missing_fields
        }

        log_event(
            agent_name="Verification Agent",
            step="verification",
            status="failed",
            message="Verification failed due to missing required fields",
            data=result
        )

        return result

    result = {
        "status": "success",
        "message": "Verification passed"
    }

    log_event(
        agent_name="Verification Agent",
        step="verification",
        status="success",
        message="Verification completed successfully",
        data=result
    )

    return result