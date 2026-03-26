from agents.audit_agent import log_event


def governance_decision_agent(verification_result: dict, failure_details: dict | None = None):
    governance_result = {
        "issue_type": "none",
        "severity": "none",
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
    issue_policy_map = {
        "missing_employee_id": {
            "severity": "low",
            "confidence": 0.92,
            "policy_decision": "auto_recover",
            "escalation_required": False,
            "escalation_reason": "Missing employee_id is covered by a deterministic fallback policy.",
        },
        "missing_email": {
            "severity": "medium",
            "confidence": 0.81,
            "policy_decision": "escalate",
            "escalation_required": True,
            "escalation_reason": "Email is mandatory and cannot be safely auto-generated.",
        },
        "identity_mismatch": {
            "severity": "high",
            "confidence": 0.97,
            "policy_decision": "escalate",
            "escalation_required": True,
            "escalation_reason": "Identity mismatch requires human review due to data integrity risk.",
        },
        "invalid_employee_id": {
            "severity": "low",
            "confidence": 0.88,
            "policy_decision": "auto_recover",
            "escalation_required": False,
            "escalation_reason": "Invalid employee_id format can be corrected using fallback generation.",
        },
        "duplicate_employee_id": {
            "severity": "medium",
            "confidence": 0.85,
            "policy_decision": "recover_with_warning",
            "escalation_required": False,
            "escalation_reason": "Duplicate employee_id can be replaced with a new generated identifier.",
        },
    }

    policy = issue_policy_map.get(
        issue_type,
        {
            "severity": "medium",
            "confidence": 0.5,
            "policy_decision": "escalate",
            "escalation_required": True,
            "escalation_reason": "Unhandled issue requires manual review.",
        },
    )

    governance_result = {
        "issue_type": issue_type,
        "severity": policy["severity"],
        "confidence": policy["confidence"],
        "policy_decision": policy["policy_decision"],
        "escalation_required": policy["escalation_required"],
        "escalation_reason": policy["escalation_reason"],
    }

    log_event(
        agent_name="Governance Agent",
        step="governance_decision",
        status="success",
        message=f"Governance policy evaluated: {governance_result['policy_decision']}",
        data=governance_result,
    )

    return governance_result
