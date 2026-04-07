---
title: Clinical Deviation Environment
emoji: 🧪
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
tags:
  - openenv
---

# Clinical Deviation Environment

A structured OpenEnv-compatible environment simulating real-world deviation handling workflows in clinical bioequivalence (BE) studies.

This environment models how operators handle protocol deviations in sample collection and processing, including identifying issues, safeguarding downstream workflows, ensuring traceability, capturing documentation, and closing cases correctly.

---

## Why This Is Not a Toy Environment

This environment represents real operational workflows in regulated clinical studies. The agent must:

- Interpret structured case data
- Apply protocol rules (e.g., tolerance windows)
- Take safety-critical actions (e.g., hold processing)
- Maintain traceability across sample relationships
- Request and record missing documentation
- Escalate when required
- Close cases with correct disposition

Incorrect decisions can lead to unsafe states (e.g., allowing processing under deviation), which are penalized. The task is not classification — it is workflow execution.

---

## Observation Space

Each step returns a structured observation:

- `case_id`: Unique identifier for the case
- `task_type`: Type of workflow (timing_deviation, sample_mismatch, hemolysis)
- `study_id`: Study identifier
- `subject_id`: Subject identifier
- `current_stage`: Current workflow stage
- `facts`: Key scenario data (timestamps, barcodes, sample status, etc.)
- `workflow`: Current state of required actions:
  - deviation_flagged
  - reason_requested
  - reason_recorded
  - processing_hold
  - supervisor_required
  - case_closed
- `allowed_actions`: List of valid actions at this step
- `last_action_error`: Error message if previous action failed

Information is revealed progressively based on actions such as `inspect_case` and `review_protocol`.

---

## Action Space

The agent interacts through a constrained set of actions:

- `inspect_case`
- `review_protocol`
- `flag_deviation`
- `mark_within_tolerance`
- `request_reason`
- `record_reason:<code>`
- `place_hold`
- `release_hold`
- `block_separation`
- `request_rescan`
- `request_supervisor_review`
- `record_disposition:<value>`
- `escalate_case`
- `close_case`

Actions directly modify the workflow state and influence reward.

---

## Tasks

### Task 1: Blood Collection Timing Deviation (Easy)

**Objective:**
Determine whether a blood sample collection is outside protocol tolerance and take appropriate action.

**Key Elements:**
- Nominal vs actual collection time
- Tolerance window
- Processing status

**Success Criteria:**
- Correctly identify deviation
- Place processing hold if required
- Request and record reason
- Close case correctly

**Failure Modes:**
- Missing deviation
- Allowing processing when unsafe
- Closing without documentation

---

### Task 2: Parent–Child Sample Mismatch (Medium)

**Objective:**
Ensure correct traceability between parent and child samples during separation.

**Key Elements:**
- Parent barcode
- Expected child IDs
- Scanned child ID

**Success Criteria:**
- Detect mismatch
- Block separation
- Request correct sample
- Restore traceability
- Close correctly

**Failure Modes:**
- Allowing incorrect pairing
- Skipping verification
- Closing without resolving mismatch

---

### Task 3: Hemolyzed Sample Handling (Hard)

**Objective:**
Handle a compromised sample requiring supervisor review before storage or disposition.

**Key Elements:**
- Sample quality status (hemolyzed)
- Storage workflow
- Supervisor dependency

**Success Criteria:**
- Identify quality issue
- Place storage hold
- Request supervisor review
- Record disposition
- Close case correctly

**Failure Modes:**
- Proceeding to storage prematurely
- Skipping review
- Incorrect disposition

---

## Reward Design

The environment uses dense reward shaping:

- Rewards incremental progress toward correct workflow completion
- Penalizes unsafe or premature actions
- Penalizes repeated or irrelevant actions
- Encourages correct sequencing of actions

### Example Reward Breakdown

**Task 1:**
- Identify deviation: +0.20
- Place hold: +0.20
- Request reason: +0.15
- Record reason: +0.10
- Correct closure: +0.15
- Unsafe action: -0.25
- Premature closure: -0.10

Rewards are cumulative and capped between 0.0 and 1.0.

---

## Grading

Each task uses a deterministic grader with a checklist:

- deviation_identified
- workflow_safeguarded
- documentation_complete
- correct_disposition
- unsafe_action_taken

Final score is computed as:

```
score = weighted_sum(checklist_items)
score = max(0.0, min(score, 1.0))
```

Grading is reproducible and does not depend on randomness.

---

## API Endpoints

### GET /tasks

Returns available tasks with metadata:

```json
[
  {
    "id": "timing_deviation",
    "difficulty": "easy",
    "description": "Blood collection timing deviation"
  }
]
```

---

### POST /reset

Resets environment for a task:

```json
{
  "task_id": "timing_deviation"
}
```

---

### POST /step

Takes an action:

```json
{
  "action": "flag_deviation"
}
```

Returns observation, reward, and done flag.

---

### GET /state

Returns current state:

```json
{
  "observation": {...},
  "reward": 0.4,
  "done": false,
  "steps": 3
}
```

---

### GET /grader

Returns final evaluation:

```json
{
  "score": 0.85,
  "success": true,
  "details": {...}
}
```

---

## Running Locally

```bash
docker build -t clinical-deviation-env .
docker run -p 8000:8000 clinical-deviation-env
```

---

## Inference

The project includes a required `inference.py` script at the root.

### Required Environment Variables

- `API_BASE_URL` (default provided)
- `MODEL_NAME` (default provided)
- `HF_TOKEN` (required)

The script logs execution using:

- `[START]`
- `[STEP]`
- `[END]`

These logs are required for evaluation.

---

## Baseline Performance


- Timing Deviation: 1.00
- Sample Mismatch: 1.00
- Hemolyzed Sample: 1.00

**Average Score:** 1.00

---

## Notes

- Built for OpenEnv compatibility
- Designed for reinforcement learning workflows
- Optimized for deterministic evaluation
- Runs within hackathon constraints (CPU-only, low memory)

---