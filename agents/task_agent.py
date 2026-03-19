from agents.audit_agent import log_event


def task_agent(data: dict):
    task_result = {
        "status": "completed",
        "message": "Employee onboarding workflow completed successfully",
        "final_employee_id": data.get("employee_id"),
        "candidate_name": data.get("candidate_name")
    }

    log_event(
        agent_name="Task Agent",
        step="workflow_completion",
        status="success",
        message="Workflow completed successfully",
        data=task_result
    )

    return task_result