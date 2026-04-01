import os

import requests

from agents.audit_agent import log_event


DEFAULT_RECOVERY_EXPLANATION = (
    "FlowGuard AI applied a deterministic fallback recovery path to keep the "
    "workflow moving safely when required data was missing."
)
OPENAI_API_URL = "https://api.openai.com/v1/responses"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def _generate_default_explanation(issue_type: str, recovery_action: str):
    return (
        f"{DEFAULT_RECOVERY_EXPLANATION} Issue detected: {issue_type}. "
        f"Recovery action taken: {recovery_action}."
    )


def _generate_llm_explanation(data: dict, failure_info: dict, recovery_action: str, updated_data: dict):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    prompt = (
        "You are generating a brief recovery explanation for a workflow automation audit log. "
        "Explain what went wrong, what fallback was applied, and why the workflow can continue. "
        "Keep it under 60 words and professional.\n\n"
        f"Original data: {data}\n"
        f"Failure info: {failure_info}\n"
        f"Recovery action: {recovery_action}\n"
        f"Updated data: {updated_data}\n"
    )

    response = requests.post(
        OPENAI_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENAI_MODEL,
            "input": prompt,
        },
        timeout=15,
    )
    response.raise_for_status()

    payload = response.json()
    return (payload.get("output_text") or "").strip() or None


def auto_fix(data: dict):
    final_data = data.copy()
    employee_id = str(final_data.get("employee_id", "") or "").strip()

    if employee_id and not employee_id.startswith("EMP-"):
        final_data["employee_id"] = f"EMP-{employee_id}"
        return final_data, "Normalized employee ID format to the approved EMP- pattern"

    return final_data, "No automated recovery action applied"


def recovery_agent(data: dict, failure_info: dict):
    governance_result = failure_info.get("governance_result", {})
    issue_type = failure_info.get("details", {}).get("issue_type")
    risk_level = governance_result.get("risk_level", "MEDIUM")
    field_name = governance_result.get("field_name")

    if not failure_info.get("failure_detected"):
        recovery_result = {
            "status": "NOT_REQUIRED",
            "recovered": False,
            "recovery_action": "No recovery needed",
            "recovery_explanation": "Workflow completed without recovery.",
        }

        log_event(
            agent_name="Recovery Agent",
            step="recovery",
            status="success",
            message="No recovery action required",
            data={
                **recovery_result,
                "updated_data": data.copy(),
            },
        )

        return {
            "final_data": data.copy(),
            "recovery_result": recovery_result,
        }

    if risk_level == "HIGH":
        reason = (
            "Employee ID is a critical identity field and cannot be auto-generated."
            if field_name == "employee_id"
            else f"{field_name or 'This field'} is critical and requires human verification."
        )
        recovery_result = {
            "status": "ESCALATED",
            "recovered": False,
            "recovery_action": "Escalated",
            "message": "Critical field missing. Requires human verification.",
            "reason": reason,
            "recovery_explanation": "Issue required human review due to governance policy.",
        }

        log_event(
            agent_name="Recovery Agent",
            step="recovery",
            status="failed",
            message="Recovery blocked by governance policy; escalation required",
            data={
                **recovery_result,
                "updated_data": data.copy(),
            },
        )

        return {
            "final_data": data.copy(),
            "recovery_result": recovery_result,
        }

    if risk_level == "MEDIUM":
        recovery_result = {
            "status": "REVIEW_REQUIRED",
            "recovered": False,
            "recovery_action": "Review required",
            "message": "Suggested fix available but needs approval.",
            "recovery_explanation": "Workflow paused for human approval before any fix is applied.",
        }

        log_event(
            agent_name="Recovery Agent",
            step="recovery",
            status="pending_review",
            message="Recovery requires human approval before changes can be applied",
            data={
                **recovery_result,
                "updated_data": data.copy(),
            },
        )

        return {
            "final_data": data.copy(),
            "recovery_result": recovery_result,
        }

    final_data, recovery_action = auto_fix(data)
    recovery_explanation = _generate_default_explanation(issue_type or "workflow_issue", recovery_action)

    try:
        llm_explanation = _generate_llm_explanation(
            data=data,
            failure_info=failure_info,
            recovery_action=recovery_action,
            updated_data=final_data,
        )
        if llm_explanation:
            recovery_explanation = llm_explanation
    except Exception as exc:
        log_event(
            agent_name="Recovery Agent",
            step="recovery_explanation",
            status="failed",
            message="OpenAI explanation generation failed; using default explanation",
            data={"error": str(exc)},
        )

    recovery_result = {
        "status": "AUTO_FIXED",
        "recovered": True,
        "recovery_action": recovery_action,
        "recovery_explanation": recovery_explanation,
    }

    log_event(
        agent_name="Recovery Agent",
        step="recovery",
        status="success",
        message="Recovery action executed successfully",
        data={
            **recovery_result,
            "updated_data": final_data.copy(),
        },
    )

    return {
        "final_data": final_data,
        "recovery_result": recovery_result,
    }
