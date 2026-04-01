from agents.audit_agent import log_event


CRITICAL_FIELDS = ["employee_id", "aadhaar", "pan"]


def classify_risk(issue_type, field_name, value):
    if field_name in CRITICAL_FIELDS:
        if value is None or value == "":
            return "HIGH"

    if issue_type == "identity_mismatch":
        return "HIGH"

    if issue_type == "format_error":
        return "LOW"

    return "MEDIUM"


def _resolve_field_context(verification_result: dict) -> tuple[str | None, object]:
    issue_type = verification_result.get("issue_type")
    data = verification_result.get("data", {})

    field_map = {
        "missing_employee_id": "employee_id",
        "invalid_employee_id": "employee_id",
        "duplicate_employee_id": "employee_id",
        "missing_email": "email",
        "identity_mismatch": "employee_id",
    }

    field_name = verification_result.get("field_name") or field_map.get(issue_type)
    value = data.get(field_name) if isinstance(data, dict) and field_name else None
    return field_name, value


def governance_decision_agent(verification_result: dict, failure_details: dict | None = None):
    governance_result = {
        "issue_type": "none",
        "field_name": None,
        "severity": "none",
        "risk_level": "NONE",
        "confidence": 1.0,
        "policy_decision": "no_action",
        "escalation_required": False,
        "escalation_reason": "No escalation needed.",
    }

    if verification_result.get("status") != "failed":
        log_event(
            agent_name="Governance Agent",
            step="governance_decision",
            status="success",
            message="No governance intervention required",
            data=governance_result,
        )
        return governance_result

    issue_type = verification_result.get("issue_type", "workflow_issue")
    field_name, field_value = _resolve_field_context(verification_result)
    normalized_issue_type = "format_error" if issue_type == "invalid_employee_id" else issue_type
    risk_level = classify_risk(normalized_issue_type, field_name, field_value)

    if risk_level == "HIGH":
        policy_decision = "escalate"
        escalation_required = True
        escalation_reason = (
            f"{field_name} is a critical identity field and cannot be auto-generated."
            if field_name in CRITICAL_FIELDS
            else "Issue requires human review due to data integrity risk."
        )
        confidence = 0.97 if issue_type == "identity_mismatch" else 0.95
    elif risk_level == "MEDIUM":
        policy_decision = "review_required"
        escalation_required = True
        escalation_reason = "Suggested fix may exist, but human approval is required before any change."
        confidence = 0.85
    else:
        policy_decision = "auto_recover"
        escalation_required = False
        escalation_reason = "Issue is low risk and can be auto-corrected safely."
        confidence = 0.88

    governance_result = {
        "issue_type": issue_type,
        "field_name": field_name,
        "severity": risk_level.lower(),
        "risk_level": risk_level,
        "confidence": confidence,
        "policy_decision": policy_decision,
        "escalation_required": escalation_required,
        "escalation_reason": escalation_reason,
    }

    log_event(
        agent_name="Governance Agent",
        step="governance_decision",
        status="success",
        message=f"Governance policy evaluated: {governance_result['policy_decision']}",
        data=governance_result,
    )

    return governance_result
