# FlowGuard AI - Autonomous Workflow Recovery System

## Live Demo

https://flowguard-ai.streamlit.app/

## GitHub Repo

https://github.com/AasthaSingh2/FlowGuard-AI-Autonomous-Workflow-Recovery-System

## Problem Statement

Enterprise workflows often fail due to:

- Missing or inconsistent data
- Duplicate records
- Identity mismatches
- Manual errors

These failures:

- Delay operations
- Require manual intervention
- Increase operational costs

Existing systems detect failures but cannot recover intelligently.

## Solution

FlowGuard AI is an Agentic AI system that:

- Executes workflows autonomously
- Detects failures in real time
- Applies governance-based decisions
- Recovers workflows when safe
- Escalates high-risk cases
- Maintains a complete audit trail

## Key Features

- Multi-agent workflow system
- Real-time failure detection
- Governance-based decision engine
- Autonomous recovery where applicable
- Intelligent escalation for high-risk cases
- Before vs After workflow comparison
- Full audit trail for transparency
- Trust and safety indicators

## System Architecture

```text
User Upload
   |
Document Agent -> Extract Data
   |
Verification Agent -> Validate Fields
   |
Failure Detection Agent -> Identify Issues
   |
Governance Agent -> Decide (Recover / Escalate)
   |
Recovery Agent (if applicable)
   |
Task Agent -> Complete Workflow
   |
Audit Agent -> Log Everything
```

## Agents in the System

| Agent | Role |
|---|---|
| Document Agent | Extracts structured data from documents |
| Verification Agent | Validates required fields |
| Failure Detection Agent | Detects workflow failures |
| Governance Agent | Applies decision logic |
| Recovery Agent | Fixes recoverable issues |
| Task Agent | Completes workflow |
| Audit Agent | Logs all actions |

## Supported Demo Scenarios

### 1. Missing Employee ID

- Auto-generated ID
- Workflow recovered

### 2. Duplicate Employee ID

- New ID generated
- Recovery with warning

### 3. Missing Email

- Cannot auto-fix
- Escalated for manual review

### 4. Identity Mismatch

- High-risk case
- Escalated immediately

### 5. No Issues

- Workflow completed successfully

## Decision Logic

- IF risk = high -> Escalate
- IF issue is fixable -> Recover
- IF no issue -> Approve

## Output Example

```json
{
  "workflow_status": "completed",
  "recovery_applied": true,
  "risk_level": "medium",
  "audit_trail_completed": true
}
```

## Trust and Governance Layer

FlowGuard AI ensures:

- Policy compliance
- Data integrity
- Explainable decisions
- Complete auditability

## Audit Trail Example

```text
[1] Document Uploaded -> Success
[2] Data Extracted -> Success
[3] Verification -> Failed (Duplicate ID)
[4] Governance Decision -> Recover
[5] Recovery Applied -> New ID Generated
[6] Workflow Completed -> Success
```

## Tech Stack

- Frontend: Streamlit
- Backend Logic: Python (Agent-based architecture)
- PDF Parsing: pypdf
- Deployment: Streamlit Cloud

## How to Run Locally

```bash
git clone https://github.com/AasthaSingh2/FlowGuard-AI-Autonomous-Workflow-Recovery-System
cd FlowGuard-AI-Autonomous-Workflow-Recovery-System

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Live Demo

https://flowguard-ai.streamlit.app/

Try uploading different test cases and observe:

- Failure detection
- Decision-making
- Recovery vs Escalation
- Audit trail

## Impact

- Workflow time: 3 days -> 4 hours
- Manual effort reduced significantly
- Cost savings for enterprises
- Full transparency and traceability

## Why This Project Stands Out

FlowGuard AI is not just automation - it is:

- Decision Intelligence System
- Self-healing Workflow Engine
- Governance-aware AI System
