import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from agents.document_agent import document_agent
from agents.verification_agent import verification_agent
from agents.failure_agent import failure_detection_agent
from agents.recovery_agent import recovery_agent
from agents.task_agent import task_agent
from utils.storage import (
    get_audit_logs,
    clear_audit_logs,
    save_workflow_state,
)

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
    verification_result = verification_agent(extracted_data)
    failure_result = failure_detection_agent(verification_result)

    final_data = extracted_data

    if failure_result.get("failure_detected"):
        final_data = recovery_agent(extracted_data, failure_result)
        re_verification_result = verification_agent(final_data)
    else:
        re_verification_result = verification_result

    workflow_result = task_agent(final_data)

    final_response = {
        "uploaded_file": file.filename,
        "extracted_data": extracted_data,
        "initial_verification": verification_result,
        "failure_result": failure_result,
        "final_data": final_data,
        "final_verification": re_verification_result,
        "workflow_result": workflow_result,
        "audit_logs": get_audit_logs()
    }

    save_workflow_state(final_response)

    return final_response