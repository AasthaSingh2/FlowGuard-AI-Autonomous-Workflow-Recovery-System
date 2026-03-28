from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from workflow_service import (
    get_audit_logs_data,
    process_workflow_file,
    reset_audit_logs_data,
)

app = FastAPI(title="FlowGuard AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "FlowGuard AI backend is running"}


@app.get("/logs")
def fetch_logs():
    return get_audit_logs_data()


@app.post("/reset")
def reset_logs():
    return reset_audit_logs_data()


@app.post("/process-workflow")
async def process_workflow(file: UploadFile = File(...)):
    return process_workflow_file(file)
