from agents.audit_agent import log_event


EXISTING_EMPLOYEE_IDS = {"EMP-1001", "EMP-2024", "EMP-7777"}


def _normalize_email_prefix(email: str) -> str:
    local_part = str(email).split("@", 1)[0]
    return "".join(ch for ch in local_part.lower() if ch.isalnum())


def _extract_first_name(candidate_name: str) -> str:
    first_name = str(candidate_name).strip().split(" ", 1)[0]
    return "".join(ch for ch in first_name.lower() if ch.isalnum())


def verification_agent(data: dict):
    candidate_name = str(data.get("candidate_name", "") or "").strip()
    email = str(data.get("email", "") or "").strip()
    employee_id = str(data.get("employee_id", "") or "").strip()

    missing_fields = []
    if not candidate_name:
        missing_fields.append("candidate_name")
    if not email:
        missing_fields.append("email")
    if not employee_id:
        missing_fields.append("employee_id")

    issue_type = None
    details = "No validation issues detected."

    if not employee_id:
        issue_type = "missing_employee_id"
        details = "employee_id is missing or empty."
    elif not email:
        issue_type = "missing_email"
        details = "email is missing or empty."
    else:
        email_prefix = _normalize_email_prefix(email)
        first_name = _extract_first_name(candidate_name)

        if candidate_name and email and first_name and first_name not in email_prefix:
            issue_type = "identity_mismatch"
            details = "candidate_name does not match the email prefix."
        elif employee_id and not (
            employee_id.startswith("EMP-") or employee_id.startswith("FG-AUTO-")
        ):
            issue_type = "invalid_employee_id"
            details = "employee_id must start with EMP- or FG-AUTO-."
        elif employee_id in EXISTING_EMPLOYEE_IDS:
            issue_type = "duplicate_employee_id"
            details = "employee_id already exists in the simulated employee registry."

    if issue_type:
        result = {
            "status": "failed",
            "reason": "Validation failed",
            "issue_type": issue_type,
            "missing_fields": missing_fields,
            "details": details,
        }

        log_event(
            agent_name="Verification Agent",
            step="verification",
            status="failed",
            message="Verification failed due to workflow validation issues",
            data=result,
        )

        return result

    result = {
        "status": "success",
        "message": "Verification passed",
    }

    log_event(
        agent_name="Verification Agent",
        step="verification",
        status="success",
        message="Verification completed successfully",
        data=result,
    )

    return result
