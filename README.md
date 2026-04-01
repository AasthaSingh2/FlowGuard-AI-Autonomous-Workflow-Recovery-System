# FlowGuard AI - Autonomous Workflow Recovery System



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

- Critical identity field missing
- Governance blocks unsafe auto-recovery
- Workflow escalated for review

### 2. Duplicate Employee ID

- Duplicate detected
- Auto-replacement blocked for trust and identity integrity
- Workflow routed for review

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
- IF risk = medium -> Review required before any fix
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
[4] Governance Decision -> Review / Escalate
[5] Recovery Blocked -> Human Approval Required
[6] Workflow Completed -> Manual Review
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

- Missing employee ID -> escalation
- Duplicate ID -> review required
- Missing email -> review required
- Identity mismatch -> high-risk escalation


## 📸 Demo Preview
### 🔹 Upload & Start Workflow
<img width="1523" height="795" alt="image" src="https://github.com/user-attachments/assets/328d0c1a-892d-479c-8ebc-4221972fdd42" />

### 🔹 Autonomous Recovery (Duplicate ID)
<img width="1677" height="658" alt="image" src="https://github.com/user-attachments/assets/a883634e-1669-4ae0-8ed9-fbb7a0667dd2" />

### 🔹 Intelligent Escalation (High Risk)
<img width="1730" height="634" alt="image" src="https://github.com/user-attachments/assets/aced82d4-8e96-45a1-98aa-a2881c23b824" /> <img width="1526" height="687" alt="image" src="https://github.com/user-attachments/assets/26ee010b-2806-4360-a25e-fa213213e54b" />

### 🔹 Audit Trail & Explainability
<img width="1547" height="764" alt="image" src="https://github.com/user-attachments/assets/ef0fbe3a-c517-4fb2-9e02-a635784dee14" /> <img width="1495" height="695" alt="image" src="https://github.com/user-attachments/assets/491a1a6b-7e87-43a7-84fc-bf84d600a610" />
<img width="1451" height="674" alt="image" src="https://github.com/user-attachments/assets/ec8e6887-6e60-40cf-8a57-12842194cb9c" /> <img width="1516" height="773" alt="image" src="https://github.com/user-attachments/assets/58a9d495-c5b8-4d10-a18a-904b218a4d35" />


## Impact

- Workflow time: 3 days -> 4 hours
- Manual effort drastically reduced
- Cost savings for enterprises
- Full transparency and traceability

## Author 
Aastha Singh

