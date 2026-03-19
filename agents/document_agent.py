import os
from agents.audit_agent import log_event


def document_agent(file_path: str):
    filename = os.path.basename(file_path)

    extracted_data = {
        "candidate_name": "Aastha Singh",
        "email": "aastha@example.com",
        "employee_id": None,
        "documents_uploaded": [filename],
        "document_status": "parsed"
    }

    log_event(
        agent_name="Document Agent",
        step="document_extraction",
        status="success",
        message="Document parsed successfully",
        data=extracted_data
    )

    return extracted_data