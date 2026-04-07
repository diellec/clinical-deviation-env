TASKS = {
    "timing_deviation": {
        "id": "timing_deviation",
        "name": "Blood Collection Timing Deviation",
        "difficulty": "easy",
        "description": (
            "A blood sample was collected outside the permitted protocol tolerance. "
            "The agent must inspect the case, review the protocol rule, identify the "
            "deviation, place the workflow on hold, request and record the reason, "
            "and close the case correctly."
        ),
        "objective": (
            "Safely resolve an out-of-tolerance blood collection event before downstream "
            "processing continues."
        ),
        "key_risks": [
            "Deviation not identified",
            "Processing continues without hold",
            "Case closed without documentation"
        ],
        "available_actions": [
            "inspect_case",
            "review_protocol",
            "flag_deviation",
            "mark_within_tolerance",
            "request_reason",
            "record_reason:late_arrival",
            "place_hold",
            "release_hold",
            "close_case"
        ],
    },
    "sample_mismatch": {
        "id": "sample_mismatch",
        "name": "Parent–Child Sample Mismatch During Separation",
        "difficulty": "medium",
        "description": (
            "A scanned child sample does not match the selected parent sample during "
            "separation. The agent must detect the mismatch, block separation, request "
            "a rescan, restore traceability, and close the case correctly."
        ),
        "objective": (
            "Prevent incorrect parent-child linkage and restore traceability before "
            "sample separation proceeds."
        ),
        "key_risks": [
            "Incorrect parent-child pairing",
            "Separation proceeds under mismatch",
            "Case closed before traceability is restored"
        ],
        "available_actions": [
            "inspect_case",
            "review_protocol",
            "flag_deviation",
            "block_separation",
            "request_rescan",
            "record_disposition:traceability_restored",
            "close_case"
        ],
    },
    "hemolyzed_sample": {
        "id": "hemolyzed_sample",
        "name": "Hemolyzed Sample Before Storage",
        "difficulty": "hard",
        "description": (
            "A separated sample is marked hemolyzed before storage, and supervisor review "
            "has not yet been completed. The agent must flag the quality issue, place the "
            "sample on hold, request review, record disposition, and close the case "
            "correctly."
        ),
        "objective": (
            "Prevent premature storage of a compromised sample and ensure final disposition "
            "is documented after supervisor review."
        ),
        "key_risks": [
            "Storage proceeds before review",
            "Disposition missing",
            "Case closed without supervisor-dependent controls"
        ],
        "available_actions": [
            "inspect_case",
            "review_protocol",
            "flag_deviation",
            "place_hold",
            "request_supervisor_review",
            "record_disposition:reject_sample",
            "record_disposition:store_with_approval",
            "escalate_case",
            "close_case"
        ],
    },
}