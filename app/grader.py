def grade_episode(state):
    case_type = state.get("case_type")
    score = 0.0

    if case_type == "timing_deviation":
        if state.get("deviation_flagged"):
            score += 0.3
        if state.get("reason_requested"):
            score += 0.2
        if state.get("processing_on_hold"):
            score += 0.2
        if state.get("status") == "resolved_correctly":
            score += 0.3

    elif case_type == "sample_mismatch":
        if state.get("mismatch_flagged"):
            score += 0.3
        if state.get("separation_blocked"):
            score += 0.3
        if state.get("correct_child_requested"):
            score += 0.2
        if state.get("status") == "resolved_correctly":
            score += 0.2

    elif case_type == "hemolyzed_sample":
        if state.get("quality_issue_flagged"):
            score += 0.3
        if state.get("storage_on_hold"):
            score += 0.3
        if state.get("review_requested"):
            score += 0.2
        if state.get("status") == "resolved_correctly":
            score += 0.2

    return {
        "case_type": case_type,
        "score": round(score, 2),
        "status": state.get("status"),
        "steps_taken": state.get("steps_taken", [])
    }