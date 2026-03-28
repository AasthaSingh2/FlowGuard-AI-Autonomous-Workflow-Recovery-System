# FlowGuard AI - Autonomous Workflow Recovery System

FlowGuard AI is a hackathon-ready intelligent workflow reliability platform designed to detect failures, trigger automated recovery actions, and complete enterprise workflows with audit visibility. The current demo showcases how agentic AI can reduce manual intervention in employee onboarding by identifying missing data, recovering the workflow, and producing a final verified outcome.

## Live Demo

You can try the application here:

👉 https://flowguard-ai.streamlit.app/

Upload sample workflow documents and observe:

- Failure detection
- Governance decision
- Autonomous recovery
- Audit trail generation

## Problem Statement

Enterprise workflows often break because of incomplete documents, missing fields, or manual handoff delays. In high-volume operations such as HR onboarding, even a small data gap can stall downstream tasks, increase turnaround time, and create extra work for operations teams.

Organizations need a way to:

- detect workflow failure conditions early
- recover from common issues automatically
- maintain transparency through audit logs
- complete business processes without waiting for manual intervention

## Solution Overview

FlowGuard AI provides an agent-based workflow recovery system built with FastAPI and Streamlit. A document is uploaded, parsed into structured data, validated for required business fields, checked for workflow failure, and then passed through an automated recovery layer if needed. Once repaired, the workflow is re-verified and completed, while every step is recorded in an audit trail.

The result is a simple but powerful architecture for autonomous recovery in enterprise process automation.

## Key Features

- Autonomous workflow verification and recovery
- Agent-based orchestration for modular decision making
- Automatic fallback generation for missing `employee_id`
- Optional OpenAI-powered recovery explanation with safe fallback behavior
- Audit trail for every major workflow event
- Streamlit dashboard for demo-friendly visualization
- FastAPI backend for workflow processing and log access
- Business impact section for hackathon and stakeholder demos

## System Architecture

FlowGuard AI follows a lightweight agentic pipeline:

1. A user uploads a document through the Streamlit interface.
2. The FastAPI backend receives the file at `POST /process-workflow`.
3. The `Document Agent` extracts workflow-relevant structured data.
4. The `Verification Agent` checks for required fields.
5. The `Failure Detection Agent` determines whether recovery is required.
6. The `Recovery Agent` applies fallback logic and optionally generates a human-readable explanation.
7. The `Task Agent` completes the business workflow.
8. Audit logs and workflow state are stored for visibility and traceability.

## Agent Roles

### Document Agent

- Parses uploaded files
- Extracts structured onboarding information
- Logs document extraction status

### Verification Agent

- Validates required fields such as `candidate_name`, `email`, and `employee_id`
- Marks the workflow as passed or failed
- Reports missing fields for downstream recovery

### Failure Detection Agent

- Interprets verification results
- Flags workflow failure conditions
- Passes failure metadata to the recovery layer

### Recovery Agent

- Applies deterministic fallback recovery logic
- Auto-generates a temporary employee ID when missing
- Optionally uses OpenAI to generate a recovery explanation
- Continues safely even if the LLM call fails

### Task Agent

- Completes the employee onboarding workflow
- Returns the final workflow completion output
- Logs the successful completion state

### Audit Agent

- Records timestamped activity from each step
- Maintains traceability across the workflow lifecycle

## Demo Use Case: Employee Onboarding

The current demo simulates an employee onboarding workflow where a candidate document is uploaded for processing.

Example flow:

- A resume or onboarding document is uploaded
- Structured data is extracted from the document
- Required onboarding fields are verified
- If `employee_id` is missing, FlowGuard AI detects the failure
- A fallback employee ID is generated automatically
- The workflow is re-verified and completed
- A complete audit trail is displayed in the UI

This use case demonstrates how autonomous recovery can reduce operational delays in HR systems.

## Tech Stack

- Frontend: Streamlit
- Backend: FastAPI
- Language: Python
- AI / Recovery Explanation: OpenAI API with environment-based configuration
- HTTP Client: `requests`
- Storage: JSON-based local persistence for workflow state and audit logs

## Folder Structure

```text
FlowGuard AI/
|-- agents/
|   |-- audit_agent.py
|   |-- document_agent.py
|   |-- failure_agent.py
|   |-- recovery_agent.py
|   |-- task_agent.py
|   |-- verification_agent.py
|-- data/
|   |-- audit_log.json
|   |-- workflow_state.json
|-- uploads/
|-- utils/
|   |-- storage.py
|-- api.py
|-- app.py
|-- config.py
|-- requirements.txt
|-- README.md
```

## Setup Instructions

### 1. Clone the project

```bash
git clone <your-repo-url>
cd "FlowGuard AI"
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

Add your project dependencies to `requirements.txt`, then run:

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
BACKEND_URL=http://127.0.0.1:8000
OPENAI_MODEL=gpt-4.1-mini
```

`OPENAI_API_KEY` is optional. If it is not provided, the recovery agent uses a default explanation and the workflow still completes.

## How to Run

### Start the FastAPI backend

```bash
uvicorn api:app --reload
```

### Start the Streamlit frontend

```bash
streamlit run app.py
```

Once both services are running:

- FastAPI backend: `http://127.0.0.1:8000`
- Streamlit frontend: usually `http://localhost:8501`

## API Endpoints

### `GET /`

Health check endpoint.

Response:

```json
{
  "message": "FlowGuard AI backend is running"
}
```

### `POST /process-workflow`

Processes an uploaded workflow document and runs the full agent pipeline.

Input:

- `file`: uploaded PDF, DOC, DOCX, or image file

Returns:

- uploaded filename
- extracted data
- initial verification result
- failure detection result
- final recovered data
- final verification result
- workflow completion result
- audit logs

### `GET /logs`

Returns the stored audit logs.

### `POST /reset`

Clears audit logs and workflow state.

## Impact Model

FlowGuard AI is designed to demonstrate measurable operational value:

- Workflow time reduced: `3 days -> 4 hours`
- HR effort reduced: `5 hrs -> 1 hr`
- Estimated monthly savings: `Rs.2,00,000+` for 100 hires

This model illustrates how autonomous workflow recovery can create faster cycle times, lower manual effort, and better process consistency.

## Future Scope

- Support more enterprise workflows beyond onboarding
- Add richer document parsing for real PDF and image extraction
- Introduce multi-step approval and escalation flows
- Add role-based dashboards and analytics
- Persist workflow state in a production database
- Add retry policies and more recovery strategies
- Support human-in-the-loop review for high-risk failures
- Expand LLM-driven explanations and root-cause insights

---

FlowGuard AI demonstrates how agentic AI can move beyond chat and into reliable business process automation by detecting issues, recovering intelligently, and keeping workflows on track.
