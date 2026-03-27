import os

from pypdf import PdfReader

from agents.audit_agent import log_event


def _extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        # Keep the page text in its raw line-oriented form so blank
        # same-line values stay blank instead of absorbing the next field.
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def _extract_text(file_path: str) -> str:
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return _extract_pdf_text(file_path)

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file_obj:
            return file_obj.read()
    except Exception:
        return ""


def _parse_fields_from_lines(lines: list[str]) -> dict:
    extracted = {
        "candidate_name": "",
        "email": "",
        "employee_id": "",
        "document_status": "",
    }

    for line in lines:
        if line.startswith("Candidate Name:"):
            extracted["candidate_name"] = line.split(":", 1)[1].strip()
        elif line.startswith("Email:"):
            extracted["email"] = line.split(":", 1)[1].strip()
        elif line.startswith("Employee ID:"):
            extracted["employee_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("Document Status:"):
            extracted["document_status"] = line.split(":", 1)[1].strip()

    return extracted


def document_agent(file_path: str):
    filename = os.path.basename(file_path)
    raw_text = _extract_text(file_path)
    lines = [line.strip() for line in raw_text.splitlines()]
    parsed_fields = _parse_fields_from_lines(lines)

    extracted_data = {
        "candidate_name": parsed_fields["candidate_name"],
        "email": parsed_fields["email"],
        "employee_id": parsed_fields["employee_id"],
        "documents_uploaded": [filename],
        "document_status": (parsed_fields["document_status"] or "parsed").lower(),
    }

    print("RAW PDF TEXT:", raw_text)
    print("PARSED LINES:", lines)
    print("EXTRACTED DATA:", extracted_data)

    log_event(
        agent_name="Document Agent",
        step="document_extraction",
        status="success",
        message="Document parsed successfully",
        data={
            **extracted_data,
            "raw_text_preview": raw_text[:1000],
        },
    )

    return extracted_data
