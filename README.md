# FlowGuard AI - Autonomous Workflow Recovery System

**Author:** Aastha Singh

## Live Demo

https://flowguard-ai.streamlit.app/

## GitHub Repo

https://github.com/AasthaSingh2/FlowGuard-AI-Autonomous-Workflow-Recovery-System

## Problem Statement

Enterprise workflows often fail due to:

- Missing or incomplete data
- Duplicate or inconsistent records
- Identity mismatches
- Manual processing errors

These failures lead to:

- Delays in operations
- High manual intervention
- Increased operational cost
- Lack of traceability

Existing systems may detect failures, but they cannot intelligently recover them.

## Solution - FlowGuard AI

FlowGuard AI is a multi-agent, governance-aware system that:

- Takes ownership of enterprise workflows
- Detects failures in real time
- Applies policy-based decision making
- Automatically recovers safe failures
- Escalates high-risk cases
- Maintains a complete audit trail

From detection to decision, recovery, and completion, the system is designed to keep workflows moving safely and transparently.

## System Architecture

```text
Upload Document
      |
Document Agent -> Extract Data
      |
Verification Agent -> Validate Fields
      |
Failure Detection Agent -> Identify Issues
      |
Governance Agent -> Decide (Recover / Escalate)
      |
Recovery Agent (if allowed)
      |
Task Agent -> Complete Workflow
      |
Audit Agent -> Log Every Step
```

## Multi-Agent Design

| Agent | Responsibility |
|---|---|
| Document Agent | Extracts structured data from documents |
| Verification Agent | Validates required fields |
| Failure Detection Agent | Detects workflow issues |
| Governance Agent | Applies policy-based decisions |
| Recovery Agent | Fixes recoverable issues |
| Task Agent | Completes workflow execution |
| Audit Agent | Logs all actions and decisions |

## Supported Workflow Scenarios

### 1. Missing Employee ID

- Issue detected
- System generates a new ID
- Workflow recovered automatically

### 2. Duplicate Employee ID

- Duplicate detected
- New ID generated
- Recovery applied with warning

### 3. Missing Email

- Critical data missing
- Unsafe to auto-fix
- Workflow escalated

### 4. Identity Mismatch

- High-risk inconsistency detected
- No recovery allowed
- Immediate escalation

### 5. No Issues

- All fields valid
- Workflow completed successfully

## Decision Intelligence

Core logic:

- IF risk = high -> Escalate
- IF issue is safe to fix -> Recover
- IF no issue -> Complete workflow

## Governance and Trust Layer

FlowGuard AI ensures:

- Policy compliance
- Risk-based decision making
- Explainable outcomes
- Controlled recovery
- Safe escalation

## Audit Trail

Every step is logged for full traceability and accountability:

```text
[1] Document Uploaded -> Success
[2] Data Extracted -> Success
[3] Verification -> Failed (Duplicate ID)
[4] Governance Decision -> Recover
[5] Recovery Applied -> New ID Generated
[6] Workflow Completed -> Success
```

## Key Features

- Multi-agent workflow orchestration
- Real-time failure detection
- Governance-based decision engine
- Autonomous recovery system
- Intelligent escalation for high-risk cases
- Before vs After comparison
- Complete audit trail
- Trust and safety indicators

## Tech Stack

- Frontend: Streamlit
- Core Logic: Python (Agent-based architecture)
- PDF Processing: pypdf
- Deployment: Streamlit Cloud

## How to Run Locally

```bash
git clone https://github.com/AasthaSingh2/FlowGuard-AI-Autonomous-Workflow-Recovery-System
cd FlowGuard-AI-Autonomous-Workflow-Recovery-System

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt
streamlit run app.py
```

## Live Demo

https://flowguard-ai.streamlit.app/

Try:

- Missing employee ID -> auto recovery
- Duplicate ID -> governed recovery
- Missing email -> escalation
- Identity mismatch -> high-risk escalation

## Impact

- Workflow time: 3 days -> 4 hours
- Manual effort drastically reduced
- Cost savings for enterprises
- Full transparency and traceability

## Author 
Aastha Singh

