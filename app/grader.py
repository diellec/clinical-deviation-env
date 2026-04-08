from copy import deepcopy


def bounded_score(score: float, eps: float = 0.01) -> float:
    if score <= eps:
        return eps
    if score >= 1.0 - eps:
        return 1.0 - eps
    return float(score)


def grade_episode(state):
    task_id = state.get("task_id")
    grader = state.get("grader", {})
    workflow = state.get("workflow", {})

    score = 0.0
    penalties = 0.0

    if task_id == "timing_deviation":
        if grader.get("issue_identified"):
            score += 0.25
        if grader.get("workflow_safeguarded"):
            score += 0.25
        if workflow.get("reason_requested") and workflow.get("reason_recorded"):
            score += 0.20
        if grader.get("correct_disposition"):
            score += 0.30

    elif task_id == "sample_mismatch":
        if grader.get("issue_identified"):
            score += 0.25
        if grader.get("workflow_safeguarded"):
            score += 0.25
        if workflow.get("correct_child_requested") and workflow.get("traceability_restored"):
            score += 0.20
        if grader.get("correct_disposition"):
            score += 0.30

    elif task_id == "hemolyzed_sample":
        if grader.get("issue_identified"):
            score += 0.25
        if grader.get("workflow_safeguarded"):
            score += 0.25
        if workflow.get("supervisor_review_requested") and workflow.get("disposition_recorded"):
            score += 0.20
        if grader.get("correct_disposition"):
            score += 0.30

    if grader.get("unsafe_action_taken"):
        penalties += 0.40

    raw_score = score - penalties
    final_score = bounded_score(raw_score)

    return {
        "task_id": task_id,
        "score": round(final_score, 2),
        "success": state.get("status") == "resolved_correctly",
        "status": state.get("status"),
        "steps_taken": state.get("steps_taken", []),
        "checklist": {
            "issue_identified": grader.get("issue_identified", False),
            "workflow_safeguarded": grader.get("workflow_safeguarded", False),
            "documentation_complete": grader.get("documentation_complete", False),
            "correct_disposition": grader.get("correct_disposition", False),
            "unsafe_action_taken": grader.get("unsafe_action_taken", False),
        },
        "workflow_snapshot": deepcopy(workflow),
        "penalties": {
            "unsafe_action_penalty": round(penalties, 2),
        },
    }