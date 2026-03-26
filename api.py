import os
import shutil

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from agents.audit_agent import log_event
from agents.document_agent import document_agent
from agents.failure_agent import failure_detection_agent
from agents.governance_agent import governance_decision_agent
from agents.recovery_agent import recovery_agent
from agents.task_agent import task_agent
from agents.verification_agent import verification_agent
from utils.storage import clear_audit_logs, get_audit_logs, save_workflow_state

app = FastAPI(title="FlowGuard AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "FlowGuard AI backend is running"}


@app.get("/logs")
def fetch_logs():
    return {"logs": get_audit_logs()}


@app.post("/reset")
def reset_logs():
    clear_audit_logs()
    save_workflow_state({})
    return {"message": "Audit logs and workflow state cleared successfully"}


@app.post("/process-workflow")
async def process_workflow(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

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
        else:
            workflow_result = task_agent(final_data)
    else:
        workflow_result = task_agent(final_data)

    audit_summary = {
        "workflow_status": workflow_result.get("status", "completed"),
        "risk_level": governance_result["severity"],
        "verification_status": final_verification.get("status", "failed"),
        "recovery_status": "recovered" if recovery_result.get("recovered", False) else "not_applied",
        "escalation_required": governance_result["escalation_required"],
        "audit_trail_completed": True,
    }

    final_response = {
        "uploaded_file": file.filename,
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
