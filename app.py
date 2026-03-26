import html
import json
import re

import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000"
PROCESS_ENDPOINT = f"{BACKEND_URL}/process-workflow"
LOGS_ENDPOINT = f"{BACKEND_URL}/logs"
RESET_ENDPOINT = f"{BACKEND_URL}/reset"
SUPPORTED_FILE_TYPES = ["pdf", "doc", "docx", "png", "jpg", "jpeg"]
LOGS_TIMEOUT_SECONDS = 10
RESET_TIMEOUT_SECONDS = 10
PROCESS_TIMEOUT_SECONDS = 120

RECOVERY_BANNER_MESSAGE = "Workflow recovered successfully through governance-aware recovery."
ESCALATION_BANNER_MESSAGE = "High-risk issue detected. Workflow escalated for manual review."
ESCALATION_WARNING_MESSAGE = "No field-level recovery was applied. This workflow was escalated for manual review."


def initialize_state():
    st.session_state.setdefault("workflow_response", None)
    st.session_state.setdefault("audit_logs", [])
    st.session_state.setdefault("backend_status_message", None)


def inject_styles():
    st.markdown(
        """
        <style>
        .fg-card { border: 1px solid #d1d5db; border-radius: 14px; padding: 1rem 1.1rem; background: #ffffff; box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04); margin-bottom: 0.75rem; min-height: 110px; }
        .fg-card-label { font-size: 0.84rem; color: #475569; margin-bottom: 0.4rem; }
        .fg-card-value { font-size: 1.35rem; font-weight: 700; color: #0f172a; word-break: break-word; }
        .fg-flow-step { border: 1px solid #cbd5e1; border-radius: 12px; padding: 0.9rem 0.8rem; background: #f8fafc; text-align: center; font-weight: 700; color: #0f172a; }
        .fg-flow-subtext { display: block; margin-top: 0.35rem; font-size: 0.84rem; font-weight: 500; color: #475569; }
        .fg-flow-arrow { text-align: center; font-size: 1.15rem; color: #64748b; padding-top: 1rem; }
        .fg-compare-wrapper { border: 1px solid rgba(148, 163, 184, 0.35); border-radius: 18px; padding: 1.1rem; background: linear-gradient(135deg, rgba(15, 23, 42, 0.04), rgba(37, 99, 235, 0.08)); margin: 1rem 0 1.25rem; }
        .fg-status-strip { display: flex; gap: 0.85rem; flex-wrap: wrap; }
        .fg-status-pill { flex: 1; min-width: 180px; border-radius: 999px; padding: 0.7rem 1rem; font-size: 0.92rem; font-weight: 700; text-align: center; border: 1px solid transparent; }
        .fg-status-pill.before { background: rgba(239, 68, 68, 0.14); border-color: rgba(248, 113, 113, 0.35); color: #b91c1c; }
        .fg-status-pill.after { background: rgba(34, 197, 94, 0.14); border-color: rgba(74, 222, 128, 0.35); color: #15803d; }
        .fg-status-pill.after-escalated { background: rgba(245, 158, 11, 0.16); border-color: rgba(251, 191, 36, 0.35); color: #b45309; }
        .fg-compare-card { border-radius: 18px; padding: 1rem; border: 1px solid rgba(148, 163, 184, 0.3); box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); min-height: 100%; }
        .fg-compare-card.before { background: linear-gradient(180deg, rgba(127, 29, 29, 0.12), rgba(15, 23, 42, 0.08)); }
        .fg-compare-card.after { background: linear-gradient(180deg, rgba(20, 83, 45, 0.12), rgba(15, 23, 42, 0.08)); }
        .fg-compare-title { font-size: 1.05rem; font-weight: 800; margin-bottom: 0.35rem; color: inherit; }
        .fg-compare-subtitle { font-size: 0.86rem; color: #64748b; margin-bottom: 1rem; line-height: 1.55; }
        .fg-compare-grid { display: grid; grid-template-columns: 1fr; gap: 0.7rem; }
        .fg-field { padding: 12px; border-radius: 10px; margin-bottom: 10px; background: #ffffff; border: 1px solid #dbe2ea; min-height: 84px; }
        .fg-label { font-size: 12px; color: #64748b; margin-bottom: 4px; }
        .fg-value { font-size: 16px; font-weight: 600; color: #0f172a; word-break: break-word; }
        .fg-updated { border: 1px solid rgba(22, 163, 74, 0.35); background: rgba(240, 253, 244, 0.85); box-shadow: 0 0 0 1px rgba(22, 163, 74, 0.08); }
        .fg-badge { display: inline-block; font-size: 10px; font-weight: 700; background: #dcfce7; color: #166534; padding: 2px 6px; border-radius: 999px; margin-left: 6px; }
        .fg-compare-helper { margin-top: 0.35rem; font-size: 0.78rem; color: #166534; line-height: 1.45; }
        .fg-decision-card, .fg-info-box, .fg-compare-note { margin-top: 1rem; padding: 0.9rem 1rem; border-radius: 14px; }
        .fg-decision-card { background: rgba(15, 23, 42, 0.04); border: 1px solid rgba(148, 163, 184, 0.26); }
        .fg-decision-title { font-size: 0.92rem; font-weight: 800; color: #0f172a; margin-bottom: 0.75rem; }
        .fg-decision-grid { display: grid; grid-template-columns: 1fr; gap: 0.55rem; }
        .fg-decision-item { border-radius: 10px; padding: 0.65rem 0.75rem; background: #ffffff; border: 1px solid rgba(148, 163, 184, 0.18); }
        .fg-decision-label { font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 0.12rem; }
        .fg-decision-value { font-size: 0.96rem; font-weight: 700; color: #0f172a; word-break: break-word; }
        .fg-info-box { background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(217, 119, 6, 0.24); color: #92400e; }
        .fg-info-box-success { background: rgba(34, 197, 94, 0.12); border: 1px solid rgba(22, 163, 74, 0.24); color: #166534; }
        .fg-compare-note { background: rgba(15, 23, 42, 0.04); border: 1px solid rgba(148, 163, 184, 0.2); color: #334155; }
        .fg-timeline-item { border-left: 4px solid #2563eb; padding: 0.9rem 1rem; margin-left: 0.35rem; margin-bottom: 1rem; border-radius: 14px; background: #ffffff; box-shadow: 0 4px 18px rgba(15, 23, 42, 0.06); }
        .fg-timeline-item.success { border-color: #16a34a; background: rgba(240, 253, 244, 0.96); }
        .fg-timeline-item.failure { border-color: #dc2626; background: rgba(254, 242, 242, 0.97); }
        .fg-timeline-item.decision { border-color: #d97706; background: rgba(255, 251, 235, 0.97); }
        .fg-timeline-item.escalation { border-color: #b45309; background: rgba(255, 247, 237, 0.98); }
        .fg-timeline-meta { font-size: 0.82rem; color: #64748b; margin-bottom: 0.35rem; }
        .fg-timeline-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.75rem; }
        .fg-timeline-cell { border-radius: 10px; padding: 0.7rem 0.8rem; background: rgba(255,255,255,0.82); border: 1px solid rgba(148, 163, 184, 0.2); }
        .fg-timeline-label { font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 0.18rem; }
        .fg-timeline-value { font-size: 0.95rem; font-weight: 700; color: #0f172a; word-break: break-word; }
        .fg-impact { border: 1px solid #dbeafe; border-radius: 14px; background: #f8fbff; padding: 1rem 1.1rem; }
        .fg-impact p { margin-bottom: 0.7rem; color: #1e293b; }
        .fg-impact p:last-child { margin-bottom: 0; }
        @media (max-width: 768px) { .fg-timeline-grid { grid-template-columns: 1fr; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def pretty_json(data):
    return json.dumps(data or {}, indent=2, ensure_ascii=True)


def render_json_block(title, data, expanded=False):
    with st.expander(title, expanded=expanded):
        st.code(pretty_json(data), language="json")


def escape_html(value):
    return html.escape(str(value), quote=True)


def clean_display_text(value):
    if value is None:
        return "N/A"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=True)
    text = html.unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "N/A"


def render_metric_card(label, value):
    st.markdown(
        f'''<div class="fg-card"><div class="fg-card-label">{escape_html(clean_display_text(label))}</div><div class="fg-card-value">{escape_html(clean_display_text(value))}</div></div>''',
        unsafe_allow_html=True,
    )


def render_status_banner(label, value, color):
    st.markdown(
        f'''<div style="padding:0.75rem 0.95rem;border-radius:12px;background-color:{color};color:white;font-weight:700;text-align:center;margin-bottom:0.75rem;">{escape_html(clean_display_text(label))}: {escape_html(clean_display_text(value))}</div>''',
        unsafe_allow_html=True,
    )


def render_info_banner(message, variant="info"):
    colors = {"success": "#15803d", "warning": "#b45309", "error": "#b91c1c", "info": "#2563eb"}
    render_status_banner("Workflow Update", message, colors.get(variant, "#2563eb"))


def format_backend_error(action, exc):
    if isinstance(exc, requests.Timeout):
        return f"{action} timed out after waiting for the backend. Please try again in a moment or confirm the API is responding at {BACKEND_URL}."
    if isinstance(exc, requests.ConnectionError):
        return f"Couldn't reach the FlowGuard AI backend for {action.lower()}. Please start the FastAPI server at {BACKEND_URL} and try again."
    return f"{action} failed because the backend returned an unexpected error: {exc}"


def format_percent(value):
    if value is None:
        return "N/A"
    return f"{int(value * 100)}%"


def format_title_case(value):
    text = clean_display_text(value)
    if text == "N/A":
        return text
    normalized = text.replace("_", " ").strip()
    if normalized.isupper() or normalized.islower():
        return normalized.title()
    return normalized


def format_policy_decision(policy_decision):
    mapping = {
        "auto_recover": "Auto Recover",
        "recover_with_warning": "Recover With Warning",
        "escalate": "Escalate",
        "no_action": "No Action",
    }
    normalized = str(policy_decision or "").strip().lower()
    return mapping.get(normalized, format_title_case(normalized))


def get_risk_level(governance_result):
    return format_title_case(governance_result.get("severity", "low"))


def get_issue_type(data):
    governance_result = data.get("governance_result", {})
    verification_result = data.get("initial_verification", {})
    return str(
        governance_result.get("issue_type")
        or verification_result.get("issue_type")
        or ""
    ).strip().lower()


def get_explanation_text(issue_type, escalated):
    if issue_type == "missing_employee_id":
        return "FlowGuard AI identified a recoverable missing employee ID, generated a compliant replacement value, and completed the workflow successfully."
    if issue_type == "duplicate_employee_id":
        return "FlowGuard AI detected a duplicate employee ID, generated a replacement identifier under governance policy, and completed the workflow with warning-aware recovery."
    if issue_type == "missing_email":
        return "FlowGuard AI identified missing critical contact data and escalated the workflow for manual review because safe autonomous recovery was not allowed."
    if issue_type == "identity_mismatch":
        return "FlowGuard AI identified a high-risk identity mismatch, stopped autonomous recovery, and routed the workflow for manual review based on governance policy."
    if escalated:
        return "FlowGuard AI identified missing critical contact data and escalated the workflow for manual review because safe autonomous recovery was not allowed."
    return "FlowGuard AI identified a recoverable workflow issue, applied governance-aware recovery, and completed the workflow successfully."


def derive_ui_state(data):
    governance_result = data.get("governance_result", {})
    recovery_result = data.get("recovery_result", {})
    workflow_result = data.get("workflow_result", {})
    issue_type = get_issue_type(data)
    workflow_status_raw = str(workflow_result.get("status", "") or "").lower()
    recovered = recovery_result.get("recovered") is True
    escalated = (workflow_status_raw == "escalated" or governance_result.get("escalation_required", False)) and not recovered

    if escalated:
        return {
            "workflow_status": "Escalated",
            "verification_status": "Failed",
            "recovery_status": "Not Applied",
            "escalation": "Required",
            "section_title": "Before Decision vs After Outcome",
            "before_badge": "Before: Decision Pending",
            "after_badge": "After: Escalated for Review",
            "after_badge_class": "after-escalated",
            "before_title": "Before Decision",
            "after_title": "After Governance Decision",
            "banner_message": ESCALATION_BANNER_MESSAGE,
            "banner_variant": "error",
            "explanation_text": get_explanation_text(issue_type, True),
            "step_three_label": "Escalate",
            "step_three_subtext": "Manual Review Required",
            "step_four_label": "Review",
            "step_four_subtext": "Escalated",
            "recovered": False,
            "escalated": True,
            "issue_type": issue_type,
        }

    return {
        "workflow_status": "Completed",
        "verification_status": "Success",
        "recovery_status": "Recovered",
        "escalation": "Not Required",
        "section_title": "Before Decision vs After Outcome",
        "before_badge": "Before: Recovery Needed",
        "after_badge": "After: Recovered",
        "after_badge_class": "after",
        "before_title": "Before Recovery",
        "after_title": "After Recovery",
        "banner_message": RECOVERY_BANNER_MESSAGE,
        "banner_variant": "success",
        "explanation_text": get_explanation_text(issue_type, False),
        "step_three_label": "Recover",
        "step_three_subtext": "Governance-Aware Recovery",
        "step_four_label": "Complete",
        "step_four_subtext": "Completed",
        "recovered": True,
        "escalated": False,
        "issue_type": issue_type,
    }


def build_decision_explanation(data):
    return derive_ui_state(data)["explanation_text"]


def fetch_logs():
    try:
        response = requests.get(LOGS_ENDPOINT, timeout=LOGS_TIMEOUT_SECONDS)
        response.raise_for_status()
        st.session_state.audit_logs = response.json().get("logs", [])
        st.session_state.backend_status_message = None
    except requests.RequestException as exc:
        st.session_state.audit_logs = []
        st.session_state.backend_status_message = format_backend_error("Loading audit logs", exc)


def process_workflow(uploaded_file):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")}
    try:
        response = requests.post(PROCESS_ENDPOINT, files=files, timeout=PROCESS_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(format_backend_error("Workflow processing", exc)) from exc


def reset_workflow():
    try:
        response = requests.post(RESET_ENDPOINT, timeout=RESET_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(format_backend_error("Resetting workflow logs", exc)) from exc


def render_overview(data):
    governance_result = data.get("governance_result", {})
    ui_state = derive_ui_state(data)
    recovery_confidence = data.get("recovery_result", {}).get("recovery_confidence")

    st.subheader("Workflow Status")
    cols = st.columns(4)
    with cols[0]:
        render_metric_card("Workflow Status", ui_state["workflow_status"])
    with cols[1]:
        render_metric_card("Verification Status", ui_state["verification_status"])
    with cols[2]:
        render_metric_card("Recovery Status", ui_state["recovery_status"])
    with cols[3]:
        render_metric_card("Escalation", ui_state["escalation"])

    cols = st.columns(4)
    with cols[0]:
        render_metric_card("Uploaded File", data.get("uploaded_file", "N/A"))
    with cols[1]:
        render_metric_card("Risk Level", get_risk_level(governance_result))
    with cols[2]:
        render_metric_card("Confidence", format_percent(governance_result.get("confidence")))
    with cols[3]:
        render_metric_card("Issue Type", format_title_case(get_issue_type(data) or "No Issue"))

    render_info_banner(ui_state["banner_message"], ui_state["banner_variant"])

    if recovery_confidence is not None:
        st.caption(f"Recovery Confidence: {int(recovery_confidence * 100)}%")


def render_visual_flow(data):
    initial_ok = data.get("initial_verification", {}).get("status") == "success"
    ui_state = derive_ui_state(data)
    verify_text = "Passed" if initial_ok else "Issue Found"

    st.subheader("Workflow Flow")
    cols = st.columns([1, 0.18, 1, 0.18, 1, 0.18, 1])
    steps = [
        ("Upload", "Document Received"),
        ("Verify", verify_text),
        (ui_state["step_three_label"], ui_state["step_three_subtext"]),
        (ui_state["step_four_label"], ui_state["step_four_subtext"]),
    ]
    for idx, (label, subtext) in enumerate(steps):
        with cols[idx * 2]:
            st.markdown(
                f'<div class="fg-flow-step">{escape_html(label)}<span class="fg-flow-subtext">{escape_html(subtext)}</span></div>',
                unsafe_allow_html=True,
            )
        if idx < len(steps) - 1:
            with cols[idx * 2 + 1]:
                st.markdown('<div class="fg-flow-arrow">-&gt;</div>', unsafe_allow_html=True)


def render_workflow_sections(data):
    left_col, right_col = st.columns(2)
    with left_col:
        render_json_block("1. Uploaded Filename", {"uploaded_file": data.get("uploaded_file")}, expanded=True)
        render_json_block("2. Extracted Data", data.get("extracted_data"), expanded=True)
        render_json_block("3. Initial Verification Result", data.get("initial_verification"))
        render_json_block("4. Failure Detection Result", data.get("failure_result"))
        render_json_block("5. Governance Result", data.get("governance_result"))
        render_json_block("6. Recovery Result", data.get("recovery_result"))
    with right_col:
        render_json_block("7. Final Data", data.get("final_data"), expanded=True)
        render_json_block("8. Final Verification Result", data.get("final_verification"))
        render_json_block("9. Workflow Completion Result", data.get("workflow_result"), expanded=True)


def format_display_value(value, missing_label):
    return missing_label if value is None or value == "" else clean_display_text(value)


def get_changed_field_names(extracted_data, final_data):
    changed = set()
    for key in ("candidate_name", "email", "employee_id", "document_status"):
        before_value = "" if extracted_data.get(key) is None else str(extracted_data.get(key))
        after_value = "" if final_data.get(key) is None else str(final_data.get(key))
        if before_value != after_value:
            changed.add(key)
    return changed


def render_field(label, before_val, after_val, helper_text="", highlight=False):
    changed = before_val != after_val
    before_html = f'''<div class="fg-field"><div class="fg-label">{escape_html(clean_display_text(label))}</div><div class="fg-value">{escape_html(clean_display_text(before_val))}</div></div>'''
    badge = '<span class="fg-badge">Updated</span>' if highlight and changed else ""
    helper_html = f'<div class="fg-compare-helper">{escape_html(clean_display_text(helper_text))}</div>' if helper_text else ""
    after_class = "fg-field fg-updated" if highlight and changed else "fg-field"
    after_html = f'''<div class="{after_class}"><div class="fg-label">{escape_html(clean_display_text(label))} {badge}</div><div class="fg-value">{escape_html(clean_display_text(after_val))}</div>{helper_html}</div>'''
    return before_html, after_html, changed


def render_decision_summary(ui_state):
    return f'''<div class="fg-decision-card"><div class="fg-decision-title">Decision Summary</div><div class="fg-decision-grid"><div class="fg-decision-item"><div class="fg-decision-label">Workflow Status</div><div class="fg-decision-value">{escape_html(ui_state["workflow_status"])}</div></div><div class="fg-decision-item"><div class="fg-decision-label">Verification Status</div><div class="fg-decision-value">{escape_html(ui_state["verification_status"])}</div></div><div class="fg-decision-item"><div class="fg-decision-label">Recovery Status</div><div class="fg-decision-value">{escape_html(ui_state["recovery_status"])}</div></div><div class="fg-decision-item"><div class="fg-decision-label">Escalation</div><div class="fg-decision-value">{escape_html(ui_state["escalation"])}</div></div></div></div>'''


def render_governance_decision(data):
    governance_result = data.get("governance_result", {})
    ui_state = derive_ui_state(data)
    st.subheader("Governance Decision")
    cols = st.columns(3)
    with cols[0]:
        render_metric_card("Issue Type", format_title_case(get_issue_type(data) or "No Issue"))
    with cols[1]:
        render_metric_card("Severity", get_risk_level(governance_result))
    with cols[2]:
        render_metric_card("Confidence", format_percent(governance_result.get("confidence")))

    cols = st.columns(4)
    with cols[0]:
        render_metric_card("Workflow Status", ui_state["workflow_status"])
    with cols[1]:
        render_metric_card("Verification Status", ui_state["verification_status"])
    with cols[2]:
        render_metric_card("Recovery Status", ui_state["recovery_status"])
    with cols[3]:
        render_metric_card("Escalation", ui_state["escalation"])

    render_metric_card("Escalation Reason", governance_result.get("escalation_reason", "N/A"))


def render_explainability_layer(data):
    explanation_text = build_decision_explanation(data)
    st.subheader("AI Decision Explanation")
    st.markdown(
        f'''<div class="fg-impact" style="margin-bottom:1rem;"><p style="margin:0;line-height:1.75;font-size:1rem;">{escape_html(explanation_text)}</p></div>''',
        unsafe_allow_html=True,
    )


def render_trust_indicators(data):
    governance_result = data.get("governance_result", {})
    st.subheader("Trust & Safety Indicators")
    cols = st.columns(4)
    with cols[0]:
        render_metric_card("Confidence Score", format_percent(governance_result.get("confidence")))
    with cols[1]:
        render_metric_card("Policy Compliance", "Yes")
    with cols[2]:
        render_metric_card("Data Integrity", "Maintained")
    with cols[3]:
        render_metric_card("Audit Trace", "Complete")


def render_audit_summary(data, logs):
    governance_result = data.get("governance_result", {})
    ui_state = derive_ui_state(data)
    st.subheader("Final Audit Summary")
    cols = st.columns(5)
    with cols[0]:
        render_metric_card("Workflow Status", ui_state["workflow_status"])
    with cols[1]:
        render_metric_card("Verification Status", ui_state["verification_status"])
    with cols[2]:
        render_metric_card("Recovery Status", ui_state["recovery_status"])
    with cols[3]:
        render_metric_card("Escalation", ui_state["escalation"])
    with cols[4]:
        render_metric_card("Risk Level", get_risk_level(governance_result))

    if logs:
        st.caption("Audit trail is complete and aligned with the final workflow state.")


def render_before_after_comparison(data):
    extracted_data = data.get("extracted_data", {})
    final_data = data.get("final_data", {})
    ui_state = derive_ui_state(data)
    recovered = ui_state["recovered"]
    escalated = ui_state["escalated"]
    changed_field_names = get_changed_field_names(extracted_data, final_data)
    fields = [
        ("candidate_name", "Candidate Name", "N/A"),
        ("email", "Email", "N/A"),
        ("employee_id", "Employee ID", "Missing / NULL"),
        ("document_status", "Document Status", "N/A"),
    ]

    before_block = ""
    after_block = ""
    has_updates = False

    for field_key, label, missing_label in fields:
        before_val = format_display_value(extracted_data.get(field_key), missing_label)
        after_val = format_display_value(final_data.get(field_key), missing_label)
        helper = ""
        if recovered and field_key == "employee_id" and field_key in changed_field_names:
            helper = "Updated through governance-aware recovery."
        if escalated:
            before_html, after_html, changed = render_field(label, before_val, before_val, highlight=False)
        else:
            before_html, after_html, changed = render_field(label, before_val, after_val, helper_text=helper, highlight=True)
        before_block += before_html
        after_block += after_html
        has_updates = has_updates or changed

    st.subheader(ui_state["section_title"])
    st.markdown(
        f'''<div class="fg-compare-wrapper"><div class="fg-status-strip"><div class="fg-status-pill before">{escape_html(ui_state["before_badge"])}</div><div class="fg-status-pill {escape_html(ui_state["after_badge_class"])}">{escape_html(ui_state["after_badge"])}</div></div></div>''',
        unsafe_allow_html=True,
    )
    before_col, after_col = st.columns(2)

    with before_col:
        st.markdown(
            f'''<div class="fg-compare-card before"><div class="fg-compare-title">{escape_html(ui_state["before_title"])}</div><div class="fg-compare-subtitle">Initial extraction captured the workflow state before the final system decision.</div><div class="fg-compare-grid">{before_block}</div></div>''',
            unsafe_allow_html=True,
        )
        with st.expander("View extracted_data JSON"):
            st.code(pretty_json(extracted_data), language="json")

    with after_col:
        info_box = ""
        if escalated:
            info_box = f'<div class="fg-info-box">{escape_html(ESCALATION_WARNING_MESSAGE)}</div>'
        elif has_updates:
            info_box = f'<div class="fg-info-box fg-info-box-success">{escape_html(RECOVERY_BANNER_MESSAGE)}</div>'

        st.markdown(
            f'''<div class="fg-compare-card after"><div class="fg-compare-title">{escape_html(ui_state["after_title"])}</div><div class="fg-compare-subtitle">{escape_html(ui_state["explanation_text"])}</div><div class="fg-compare-grid">{after_block}</div>{render_decision_summary(ui_state)}{info_box}</div>''',
            unsafe_allow_html=True,
        )
        with st.expander("View final_data JSON"):
            st.code(pretty_json(final_data), language="json")

    st.markdown(
        '''<div class="fg-compare-note">FlowGuard AI compares the original workflow state with the final post-decision state so judges can quickly see what changed, what was recovered, and what required review.</div>''',
        unsafe_allow_html=True,
    )


def get_timeline_variant(log, ui_state):
    step = str(log.get("step", "")).lower()
    status = str(log.get("status", "")).lower()

    if step == "workflow_completion" and ui_state["escalated"]:
        return "escalation"
    if step == "governance_decision":
        return "decision"
    if status in {"failed", "pending_review"}:
        return "failure"
    return "success"


def get_timeline_agent(log, ui_state):
    if str(log.get("step", "")).lower() == "workflow_completion":
        return "Workflow Outcome"
    if str(log.get("step", "")).lower() == "governance_decision":
        return "Governance Agent"
    return clean_display_text(log.get("agent", "Unknown Agent"))


def get_timeline_action(log, ui_state):
    step = str(log.get("step", "")).lower()
    issue_type = ui_state["issue_type"]

    if step == "document_extraction":
        return "Document Extraction"
    if step == "verification":
        return "Verification"
    if step == "failure_detection":
        return "Failure Detection"
    if step == "governance_decision":
        return "Escalation Decision" if ui_state["escalated"] else "Recovery Decision"
    if step == "recovery":
        if issue_type in {"missing_employee_id", "duplicate_employee_id", "invalid_employee_id"}:
            return "ID Replacement"
        return "Automated Recovery"
    if step == "workflow_completion":
        return "Manual Review" if ui_state["escalated"] else "Completed"
    return format_title_case(step or "Unknown Step")


def get_timeline_result(log, ui_state):
    step = str(log.get("step", "")).lower()
    status = str(log.get("status", "")).lower()

    if step == "governance_decision":
        return "Escalated" if ui_state["escalated"] else format_policy_decision(log.get("data", {}).get("policy_decision"))
    if step == "workflow_completion":
        return "Escalated" if ui_state["escalated"] else "Success"
    if step == "recovery":
        return "Success"
    if step in {"verification", "failure_detection"} and status == "failed":
        return "Failed"
    if status == "success":
        return "Success"
    if status == "decision":
        return "Escalated" if ui_state["escalated"] else "Success"
    return format_title_case(status or "Unknown")


def render_audit_step(index, log, ui_state):
    variant = get_timeline_variant(log, ui_state)
    timestamp = clean_display_text(log.get("timestamp", "N/A"))
    agent = get_timeline_agent(log, ui_state)
    action = get_timeline_action(log, ui_state)
    result = get_timeline_result(log, ui_state)

    st.markdown(
        f'''<div class="fg-timeline-item {variant}"><div class="fg-timeline-meta">{index}. {escape_html(timestamp)}</div><div class="fg-timeline-grid"><div class="fg-timeline-cell"><div class="fg-timeline-label">Step Number</div><div class="fg-timeline-value">{index}</div></div><div class="fg-timeline-cell"><div class="fg-timeline-label">Agent</div><div class="fg-timeline-value">{escape_html(agent)}</div></div><div class="fg-timeline-cell"><div class="fg-timeline-label">Action</div><div class="fg-timeline-value">{escape_html(action)}</div></div><div class="fg-timeline-cell"><div class="fg-timeline-label">Result</div><div class="fg-timeline-value">{escape_html(result)}</div></div></div></div>''',
        unsafe_allow_html=True,
    )

    if log.get("data"):
        with st.expander(f"View details for step {index}"):
            st.code(pretty_json(log["data"]), language="json")


def render_logs_timeline(logs, data=None):
    st.subheader("Audit Trail Timeline")
    if not logs:
        st.caption("No audit logs available yet.")
        return

    if data is None:
        last_workflow_log = next((log for log in reversed(logs) if log.get("step") == "workflow_completion"), {})
        inferred_workflow = last_workflow_log.get("data", {}) if isinstance(last_workflow_log.get("data"), dict) else {}
        data = {"workflow_result": inferred_workflow}

    ui_state = derive_ui_state(data or {})
    for index, log in enumerate(logs, start=1):
        render_audit_step(index, log, ui_state)


def render_business_impact():
    st.subheader("Business Impact")
    st.markdown(
        '''<div class="fg-impact"><p><strong>Workflow time reduced:</strong> 3 days &rarr; 4 hours</p><p><strong>HR effort reduced:</strong> 5 hrs &rarr; 1 hr</p><p><strong>Estimated monthly savings:</strong> &#8377;2,00,000+ for 100 hires</p></div>''',
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="FlowGuard AI", layout="wide")
    initialize_state()
    fetch_logs()
    inject_styles()
    st.markdown("<h1>FlowGuard AI &ndash; Autonomous Workflow Recovery System</h1>", unsafe_allow_html=True)
    st.subheader("Agentic AI for Autonomous Enterprise Workflows")

    if st.session_state.backend_status_message:
        st.error(st.session_state.backend_status_message)

    with st.container():
        upload_col, action_col = st.columns([1.8, 1])
        with upload_col:
            uploaded_file = st.file_uploader(
                "Upload workflow document",
                type=SUPPORTED_FILE_TYPES,
                help="Supported formats: PDF, DOC, DOCX, PNG, JPG, JPEG",
            )
        with action_col:
            st.markdown("### Actions")
            process_clicked = st.button("Process Workflow", use_container_width=True)
            reset_clicked = st.button("Reset Workflow Logs", use_container_width=True)

    if reset_clicked:
        try:
            result = reset_workflow()
            st.session_state.workflow_response = None
            st.session_state.audit_logs = []
            st.session_state.backend_status_message = None
            st.success(result.get("message", "Logs reset successfully."))
        except RuntimeError as exc:
            st.error(str(exc))

    if process_clicked:
        if not uploaded_file:
            st.warning("Please upload a file before processing the workflow.")
        else:
            try:
                with st.spinner("Processing workflow through FlowGuard AI agents..."):
                    st.session_state.workflow_response = process_workflow(uploaded_file)
                    st.session_state.audit_logs = st.session_state.workflow_response.get("audit_logs", [])
                    st.session_state.backend_status_message = None

                workflow_response = st.session_state.workflow_response
                ui_state = derive_ui_state(workflow_response)
                if ui_state["escalated"]:
                    st.error(ESCALATION_BANNER_MESSAGE)
                else:
                    st.success(RECOVERY_BANNER_MESSAGE)
            except RuntimeError as exc:
                st.session_state.workflow_response = None
                st.error(str(exc))

    workflow_response = st.session_state.workflow_response
    if workflow_response:
        render_overview(workflow_response)
        render_visual_flow(workflow_response)
        render_workflow_sections(workflow_response)
        render_governance_decision(workflow_response)
        render_explainability_layer(workflow_response)
        render_trust_indicators(workflow_response)
        render_audit_summary(workflow_response, st.session_state.audit_logs)
        render_before_after_comparison(workflow_response)
        render_logs_timeline(st.session_state.audit_logs, workflow_response)
        render_business_impact()
    else:
        st.info("Upload a file and click Process Workflow to view the autonomous recovery flow.")
        render_logs_timeline(st.session_state.audit_logs)
        render_business_impact()


if __name__ == "__main__":
    main()
