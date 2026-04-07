TASKS = {
    "timing_deviation": {
        "name": "Timing Deviation in Blood Collection",
        "description": (
            "A blood sample was collected outside the allowed protocol tolerance. "
            "The agent must identify the deviation, hold downstream processing, "
            "and ensure proper documentation before closure."
        ),
        "available_actions": [
            "inspect_case",
            "flag_deviation",
            "request_reason",
            "hold_processing",
            "allow_processing",
            "close_case"
        ]
    },
    "sample_mismatch": {
        "name": "Sample Mismatch During Separation",
        "description": (
            "A scanned child sample does not belong to the selected parent sample. "
            "The agent must detect the mismatch, block separation, and request the "
            "correct child sample before closure."
        ),
        "available_actions": [
            "inspect_case",
            "flag_mismatch",
            "block_separation",
            "request_correct_child",
            "allow_separation",
            "close_case"
        ]
    },
    "hemolyzed_sample": {
        "name": "Hemolyzed Sample Before Storage",
        "description": (
            "A sample has been marked hemolyzed after separation, but supervisor review "
            "has not yet occurred. The agent must flag the quality issue, hold storage, "
            "and request supervisor review before closure."
        ),
        "available_actions": [
            "inspect_case",
            "flag_quality_issue",
            "hold_storage",
            "request_supervisor_review",
            "allow_storage",
            "close_case"
        ]
    }
}