import os
from pathlib import Path
from typing import Any

from agents.audit_agent import log_event
from agents.document_agent import document_agent
from agents.failure_agent import failure_detection_agent
from agents.governance_agent import governance_decision_agent
from agents.recovery_agent import recovery_agent
from agents.task_agent import task_agent
from agents.verification_agent import verification_agent
from utils.storage import clear_audit_logs, get_audit_logs, save_workflow_state


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def _get_uploaded_filename(uploaded_file: Any) -> str:
    filename = getattr(uploaded_file, "name", None) or getattr(uploaded_file, "filename", None)
    return os.path.basename(filename or "uploaded_workflow")


def _read_uploaded_bytes(uploaded_file: Any) -> bytes:
    if hasattr(uploaded_file, "getvalue"):
        return uploaded_file.getvalue()

    file_obj = getattr(uploaded_file, "file", None)
    if file_obj is None:
        raise ValueError("Unsupported uploaded file object: missing file content.")

    if hasattr(file_obj, "seek"):
        file_obj.seek(0)
    content = file_obj.read()
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)
    return content


def _save_uploaded_file(uploaded_file: Any) -> tuple[str, str]:
    filename = _get_uploaded_filename(uploaded_file)
    file_path = UPLOAD_DIR / filename
    file_bytes = _read_uploaded_bytes(uploaded_file)
    file_path.write_bytes(file_bytes)
    return str(file_path), filename


def _build_escalated_workflow_result(extracted_data: dict) -> dict:
    workflow_result = {
        "status": "escalated",
        "message": "Workflow escalated for manual review",
        "candidate_name": extracted_data.get("candidate_name"),
    }
    log_event(
        agent_name="Task Agent",
        step="workflow_completion",
        status="decision",
        message="Workflow escalated for manual review",
        data=workflow_result,
    )
    return workflow_result


def process_workflow_file(uploaded_file: Any) -> dict:
    file_path, filename = _save_uploaded_file(uploaded_file)

    extracted_data = document_agent(file_path)
    initial_verification = verification_agent(extracted_data)
    failure_result = failure_detection_agent(initial_verification)
    governance_result = governance_decision_agent(initial_verification, failure_result)

    final_data = extracted_data.copy()
    final_verification = initial_verification
    recovery_result = {
        "recovered": False,
        "recovery_action": "No recovery needed",
        "recovery_explanation": "Workflow completed without recovery.",
    }

    if failure_result.get("failure_detected"):
        policy_decision = governance_result.get("policy_decision")

        if policy_decision in {"auto_recover", "recover_with_warning"}:
            recovery_output = recovery_agent(
                extracted_data,
                {
                    **failure_result,
                    "details": initial_verification,
                    "governance_result": governance_result,
                },
            )
            final_data = recovery_output.get("final_data", extracted_data.copy())
            recovery_result = recovery_output.get("recovery_result", recovery_result)
            final_verification = verification_agent(final_data)
            workflow_result = task_agent(final_data)
        elif policy_decision == "escalate":
            recovery_result = {
                "recovered": False,
                "recovery_action": "Escalated instead of recovered",
                "recovery_explanation": "Issue required human review due to governance policy.",
            }
            workflow_result = _build_escalated_workflow_result(extracted_data)
        else:
            workflow_result = task_agent(final_data)
    else:
        workflow_result = task_agent(final_data)

    audit_summary = {
        "workflow_status": workflow_result.get("status", "completed"),
        "risk_level": governance_result.get("severity", "none"),
        "verification_status": final_verification.get("status", "failed"),
        "recovery_status": "recovered" if recovery_result.get("recovered", False) else "not_applied",
        "escalation_required": governance_result.get("escalation_required", False),
        "audit_trail_completed": True,
    }

    final_response = {
        "uploaded_file": filename,
        "extracted_data": extracted_data,
        "initial_verification": initial_verification,
        "failure_result": failure_result,
        "governance_result": governance_result,
        "recovery_result": recovery_result,
        "final_data": final_data,
        "final_verification": final_verification,
        "workflow_result": workflow_result,
        "audit_summary": audit_summary,
        "audit_logs": get_audit_logs(),
    }

    save_workflow_state(final_response)
    return final_response


def get_audit_logs_data() -> dict:
    return {"logs": get_audit_logs()}


def reset_audit_logs_data() -> dict:
    clear_audit_logs()
    save_workflow_state({})
    return {"message": "Audit logs and workflow state cleared successfully"}
