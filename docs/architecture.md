# FlowGuard AI Architecture

## System Overview

FlowGuard AI is an agent-based workflow resilience system built to detect process failures, recover from them automatically, and complete business workflows with audit visibility. The platform combines a Streamlit frontend for interactive demo and operator visibility with a FastAPI backend that orchestrates a sequence of specialized agents.

The current implementation focuses on employee onboarding as a representative enterprise workflow. A document is uploaded, converted into structured onboarding data, validated against required fields, checked for failure conditions, and recovered if needed before the workflow is completed.

At a high level, FlowGuard AI is designed around three principles:

- modular agent responsibilities
- autonomous recovery with safe fallbacks
- transparent audit logging across the workflow lifecycle

## Frontend / Backend Flow

### Frontend

The Streamlit application acts as the user-facing control layer. It allows the user to:

- upload a workflow document
- trigger workflow processing
- reset the workflow state and audit logs
- view extracted data, verification results, recovery output, and completion status
- inspect an audit trail through a timeline-style interface

### Backend

The FastAPI backend provides the workflow execution layer. It exposes endpoints for:

- processing uploaded files through the agent pipeline
- retrieving audit logs
- resetting logs and saved workflow state

### End-to-End Interaction Flow

1. The user uploads a document in the Streamlit frontend.
2. Streamlit sends the file to `POST /process-workflow`.
3. FastAPI stores the file temporarily in the `uploads/` directory.
4. The backend runs the document through the agent pipeline.
5. A structured response is returned to Streamlit.
6. The frontend renders the workflow result, status cards, recovery output, and audit trail.

This separation keeps the UI lightweight while the backend handles orchestration and agent execution.

## Role of Each Agent

### Document Agent

The `Document Agent` is responsible for converting the uploaded file into structured workflow data. In the current demo, it simulates extracted employee onboarding fields such as:

- candidate name
- email
- employee ID
- uploaded document metadata

It also logs a successful extraction event for auditability.

### Verification Agent

The `Verification Agent` validates whether the extracted data contains all required business fields. In the onboarding flow, it checks for:

- `candidate_name`
- `email`
- `employee_id`

If any required field is missing, the agent returns a failed verification result along with the missing field list. This output is used by downstream failure detection and recovery logic.

### Failure Detection Agent

The `Failure Detection Agent` interprets verification output and determines whether the workflow is in a recoverable failure state. In the current implementation, a failed verification is translated into:

- `failure_detected = true`
- `failure_type = missing_data`
- failure details from the verification agent

This agent acts as the decision boundary between normal processing and recovery execution.

### Recovery Agent

The `Recovery Agent` performs automated remediation when a failure is detected. Its design includes:

- deterministic fallback recovery logic
- optional LLM-generated explanation
- fail-safe execution even when OpenAI is unavailable

In the current onboarding demo, if `employee_id` is missing, the recovery agent auto-generates a temporary ID. It also returns recovery metadata including:

- `recovered`
- `recovery_action`
- `recovery_explanation`
- `updated_data`

If an OpenAI API key is configured, the agent can generate a short human-readable explanation of the recovery action. If the LLM call fails, the workflow still continues using a default explanation.

### Task Agent

The `Task Agent` represents the final business action in the workflow. For the employee onboarding demo, it marks the onboarding process as completed and returns the final workflow result, including the employee ID used for completion.

### Audit Agent

The `Audit Agent` is a shared cross-cutting component used by all other agents. It records structured log entries containing:

- timestamp
- agent name
- workflow step
- status
- message
- associated data payload

This ensures every major workflow event is traceable.

## Workflow Steps

The current workflow runs in the following sequence:

1. A file is uploaded to the backend.
2. The `Document Agent` extracts structured onboarding data.
3. The `Verification Agent` checks required fields.
4. The `Failure Detection Agent` decides whether a workflow issue exists.
5. If a failure is detected, the `Recovery Agent` applies fallback remediation.
6. The updated data is re-verified by the `Verification Agent`.
7. The `Task Agent` completes the business workflow.
8. The final workflow state and audit logs are returned to the frontend and saved locally.

This creates a closed-loop flow in which the system does not only detect a problem, but also attempts recovery before completing the process.

## Failure Detection and Recovery Design

Failure handling is central to FlowGuard AI. Instead of treating validation failure as a terminal state, the architecture introduces an explicit recovery layer between failure detection and final workflow completion.

### Detection Design

Failure detection is based on business-rule validation rather than system exceptions alone. This is important in enterprise workflows because many real failures are logical or process-level, such as:

- missing required fields
- incomplete forms
- invalid downstream handoff conditions

By converting verification failures into structured failure objects, the system creates a standard interface for recovery.

### Recovery Design

The recovery layer is intentionally dual-mode:

- deterministic recovery for reliability
- LLM-generated explanation for interpretability

Deterministic fallback ensures the workflow can continue safely in a hackathon or enterprise prototype setting. The optional LLM explanation improves transparency for operators, reviewers, or auditors without making the workflow dependent on model availability.

This makes the recovery subsystem resilient by design:

- the fallback logic always works locally
- the explanation layer is additive, not critical-path
- try/except prevents LLM failure from breaking the workflow

## Audit Logging Design

Auditability is built into the architecture from the start. Every agent uses a shared logging mechanism to append structured events to a JSON audit file.

### Log Structure

Each log entry includes:

- `timestamp`
- `agent`
- `step`
- `status`
- `message`
- `data`

### Storage Design

Audit logs are persisted locally in:

- `data/audit_log.json`

Workflow state is stored in:

- `data/workflow_state.json`

The storage layer ensures data files exist before reading or writing, which keeps the demo stable and simple.

### Why Audit Logging Matters

In enterprise workflow systems, stakeholders need to know:

- what happened
- when it happened
- which component made the decision
- what recovery action was taken

FlowGuard AI addresses this by making every workflow transition observable and reviewable from the frontend and backend.

## Why This Is Agentic AI

FlowGuard AI is agentic because it is not a single prompt-response system. Instead, it is composed of multiple specialized agents that:

- operate with distinct responsibilities
- exchange structured outputs
- make stage-specific decisions
- adapt the workflow path based on intermediate results

The system demonstrates core agentic characteristics:

- decomposition of a business problem into specialized sub-tasks
- dynamic branching based on workflow state
- autonomous recovery rather than passive reporting
- persistence of decision context through audit logs and state

The Recovery Agent further extends this design by combining deterministic automation with optional LLM-assisted explanation, showing how agentic systems can mix rule-based reliability with AI-enhanced reasoning and interpretability.

## Enterprise Relevance

FlowGuard AI is highly relevant to enterprise operations because many real-world workflows fail not because systems crash, but because data is incomplete, delayed, or inconsistent.

This architecture is applicable to:

- employee onboarding
- claims processing
- procurement approvals
- vendor onboarding
- customer verification workflows
- document-driven back-office automation

Its enterprise value comes from:

- reducing manual intervention
- improving workflow completion rates
- shortening turnaround time
- creating a transparent recovery trail
- enabling safer automation in operational workflows

For a hackathon setting, FlowGuard AI demonstrates a practical path from AI experimentation to business automation. It shows how agentic design can move beyond chat interfaces and into structured, recoverable enterprise process execution.

## Summary

FlowGuard AI combines a clean frontend, a lightweight API backend, specialized agents, deterministic recovery logic, optional LLM explanation, and structured audit logging into a coherent workflow recovery architecture. The result is a submission-ready example of agentic AI applied to enterprise workflow resilience.
