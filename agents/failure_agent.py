from agents.audit_agent import log_event


def failure_detection_agent(verification_result: dict):
    if verification_result.get("status") == "failed":
        failure_info = {
            "failure_detected": True,
            "failure_type": verification_result.get("issue_type", "missing_data"),
            "details": verification_result
        }

        log_event(
            agent_name="Failure Detection Agent",
            step="failure_detection",
            status="failed",
            message="Workflow failure detected",
            data=failure_info
        )

        return failure_info

    result = {
        "failure_detected": False,
        "message": "No workflow failure detected"
    }

    log_event(
        agent_name="Failure Detection Agent",
        step="failure_detection",
        status="success",
        message="No failure detected",
        data=result
    )

    return result
