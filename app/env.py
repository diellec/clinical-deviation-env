from copy import deepcopy


def bounded_score(score: float, eps: float = 0.01) -> float:
    if score <= eps:
        return eps
    if score >= 1.0 - eps:
        return 1.0 - eps
    return float(score)


class ClinicalEnv:
    def __init__(self):
        self.state = None
        self.max_steps = 8

    def get_state(self):
        if self.state is None:
            return {"error": "No active episode. Call reset first."}

        return {
            "case_id": self.state["case_id"],
            "task_id": self.state["task_id"],
            "difficulty": self.state["difficulty"],
            "status": self.state["status"],
            "done": self.state["done"],
            "steps_taken": self.state["steps_taken"],
            "score": round(bounded_score(self.state["score"]), 2),
            "observation": self._build_observation(),
            "grader_progress": deepcopy(self.state["grader"]),
        }

    def reset(self, case_type="timing_deviation"):
        if case_type == "timing_deviation":
            self.state = self._timing_deviation_case()
        elif case_type == "sample_mismatch":
            self.state = self._sample_mismatch_case()
        elif case_type == "hemolyzed_sample":
            self.state = self._hemolyzed_sample_case()
        else:
            raise ValueError(f"Unknown case_type: {case_type}")

        return {
            "message": "Environment reset successfully.",
            "task_id": self.state["task_id"],
            "observation": self._build_observation(),
            "done": self.state["done"],
            "reward": 0.0,
        }

    def step(self, action):
        if self.state is None:
            return {"error": "Call reset first"}

        if self.state["done"]:
            return {
                "error": "Episode already completed. Call /reset to start a new episode."
            }

        self.state["last_action_error"] = None
        self.state["last_action_message"] = ""
        self.state["last_reward"] = 0.0

        self.state["steps_taken"].append(action)
        self.state["step_count"] += 1

        reward = self._apply_common_step_penalties(action)

        if self.state["task_id"] == "timing_deviation":
            reward += self._step_timing_deviation(action)
        elif self.state["task_id"] == "sample_mismatch":
            reward += self._step_sample_mismatch(action)
        elif self.state["task_id"] == "hemolyzed_sample":
            reward += self._step_hemolyzed_sample(action)
        else:
            self.state["last_action_error"] = "Unknown case type."
            reward -= 0.5

        if self.state["step_count"] >= self.max_steps and not self.state["done"]:
            self.state["done"] = True
            self.state["status"] = "max_steps_reached"
            self.state["last_action_message"] = (
                "Maximum step limit reached before correct resolution."
            )

        updated_score = self.state["score"] + reward
        self.state["score"] = bounded_score(updated_score)
        self.state["last_reward"] = round(reward, 2)

        return {
            "observation": self._build_observation(),
            "reward": round(reward, 2),
            "done": self.state["done"],
            "message": self.state["last_action_message"],
            "score": round(bounded_score(self.state["score"]), 2),
            "grader_progress": deepcopy(self.state["grader"]),
        }

    # -----------------------------
    # Case Definitions
    # -----------------------------

    def _base_state(self):
        return {
            "study_id": "BE-24-017",
            "status": "in_progress",
            "done": False,
            "step_count": 0,
            "steps_taken": [],
            "score": 0.01,
            "last_action_error": None,
            "last_action_message": "",
            "last_reward": 0.0,
            "discovered_fields": {
                "case_details": False,
                "protocol": False,
            },
            "grader": {
                "issue_identified": False,
                "workflow_safeguarded": False,
                "documentation_complete": False,
                "correct_disposition": False,
                "unsafe_action_taken": False,
            },
        }

    def _timing_deviation_case(self):
        state = self._base_state()
        state.update(
            {
                "case_id": "timing_deviation_001",
                "task_id": "timing_deviation",
                "difficulty": "easy",
                "subject_id": "S-012",
                "current_stage": "collection_review",
                "activity": "Blood Collection",
                "facts": {
                    "scheduled_time": "10:00",
                    "actual_time": "10:04",
                    "tolerance_minutes": 2,
                    "sample_status": "collected",
                    "processing_status": "pending",
                },
                "workflow": {
                    "deviation_flagged": False,
                    "reason_requested": False,
                    "reason_recorded": False,
                    "processing_hold": False,
                    "processing_allowed": False,
                    "case_closed": False,
                },
                "reason_code": None,
                "available_actions": [
                    "inspect_case",
                    "review_protocol",
                    "flag_deviation",
                    "mark_within_tolerance",
                    "request_reason",
                    "record_reason:late_arrival",
                    "place_hold",
                    "release_hold",
                    "close_case",
                ],
            }
        )
        return state

    def _sample_mismatch_case(self):
        state = self._base_state()
        state.update(
            {
                "case_id": "sample_mismatch_001",
                "task_id": "sample_mismatch",
                "difficulty": "medium",
                "subject_id": "S-021",
                "current_stage": "sample_separation",
                "activity": "Sample Separation",
                "facts": {
                    "parent_sample_id": "P-1001",
                    "expected_child_sample_ids": ["C-2001", "C-2002"],
                    "scanned_child_sample_id": "C-9999",
                    "traceability_status": "unverified",
                },
                "workflow": {
                    "mismatch_flagged": False,
                    "separation_blocked": False,
                    "correct_child_requested": False,
                    "traceability_restored": False,
                    "case_closed": False,
                },
                "available_actions": [
                    "inspect_case",
                    "review_protocol",
                    "flag_deviation",
                    "block_separation",
                    "request_rescan",
                    "record_disposition:traceability_restored",
                    "close_case",
                ],
            }
        )
        return state

    def _hemolyzed_sample_case(self):
        state = self._base_state()
        state.update(
            {
                "case_id": "hemolyzed_sample_001",
                "task_id": "hemolyzed_sample",
                "difficulty": "hard",
                "subject_id": "S-033",
                "current_stage": "pre_storage_review",
                "activity": "Sample Storage",
                "facts": {
                    "parent_sample_id": "P-3001",
                    "child_sample_id": "C-4001",
                    "sample_condition": "hemolyzed",
                    "storage_status": "pending",
                    "supervisor_review_status": "pending",
                },
                "workflow": {
                    "quality_issue_flagged": False,
                    "storage_hold": False,
                    "supervisor_review_requested": False,
                    "disposition_recorded": False,
                    "replacement_required": False,
                    "case_closed": False,
                },
                "disposition": None,
                "available_actions": [
                    "inspect_case",
                    "review_protocol",
                    "flag_deviation",
                    "place_hold",
                    "request_supervisor_review",
                    "record_disposition:reject_sample",
                    "record_disposition:store_with_approval",
                    "escalate_case",
                    "close_case",
                ],
            }
        )
        return state

    # -----------------------------
    # Observation Builder
    # -----------------------------

    def _build_observation(self):
        visible_facts = {}
        if self.state["discovered_fields"]["case_details"]:
            visible_facts = deepcopy(self.state["facts"])

        protocol_hint = None
        if self.state["discovered_fields"]["protocol"]:
            protocol_hint = self._protocol_hint()

        return {
            "case_id": self.state["case_id"],
            "task_type": self.state["task_id"],
            "study_id": self.state["study_id"],
            "subject_id": self.state["subject_id"],
            "current_stage": self.state["current_stage"],
            "facts": visible_facts,
            "workflow": deepcopy(self.state["workflow"]),
            "allowed_actions": self.state["available_actions"],
            "protocol_hint": protocol_hint,
            "last_action_error": self.state["last_action_error"],
        }

    def _protocol_hint(self):
        if self.state["task_id"] == "timing_deviation":
            return "Collection beyond protocol tolerance must be flagged, documented, and placed on hold before closure."
        if self.state["task_id"] == "sample_mismatch":
            return "Separation must not proceed unless parent-child traceability is verified."
        if self.state["task_id"] == "hemolyzed_sample":
            return "Compromised samples require storage hold and supervisor review before final disposition."
        return None

    # -----------------------------
    # Common Penalties / Utilities
    # -----------------------------

    def _apply_common_step_penalties(self, action):
        reward = 0.0

        if action not in self.state["available_actions"]:
            self.state["last_action_error"] = f"Invalid action: {action}"
            self.state["last_action_message"] = "Action is not allowed for this task."
            return -0.5

        duplicates = self.state["steps_taken"][:-1].count(action)
        if duplicates >= 1:
            reward -= 0.05 * duplicates
            self.state["last_action_message"] = "Repeated action provided limited or no value."

        return reward

    def _safe_set_message(self, message):
        if not self.state["last_action_error"]:
            self.state["last_action_message"] = message

    def _extract_value(self, action, prefix):
        if action.startswith(prefix):
            return action.split(":", 1)[1]
        return None

    # -----------------------------
    # Task 1: Timing Deviation
    # -----------------------------

    def _step_timing_deviation(self, action):
        reward = 0.0
        facts = self.state["facts"]
        workflow = self.state["workflow"]
        delay = 4
        out_of_tolerance = delay > facts["tolerance_minutes"]

        if action == "inspect_case":
            self.state["discovered_fields"]["case_details"] = True
            reward += 0.1
            self._safe_set_message(
                "Case inspected. Collection time details are now visible."
            )

        elif action == "review_protocol":
            self.state["discovered_fields"]["protocol"] = True
            reward += 0.1
            self._safe_set_message(
                "Protocol reviewed. Tolerance handling rule is now visible."
            )

        elif action == "flag_deviation":
            if out_of_tolerance:
                if not workflow["deviation_flagged"]:
                    workflow["deviation_flagged"] = True
                    self.state["grader"]["issue_identified"] = True
                    reward += 0.2
                    self._safe_set_message("Deviation flagged correctly.")
                else:
                    self._safe_set_message("Deviation was already flagged.")
            else:
                self.state["grader"]["unsafe_action_taken"] = True
                reward -= 0.2
                self._safe_set_message("No deviation should be flagged for this case.")

        elif action == "mark_within_tolerance":
            if out_of_tolerance:
                self.state["grader"]["unsafe_action_taken"] = True
                reward -= 0.25
                self._safe_set_message(
                    "Incorrectly marked an out-of-tolerance collection as acceptable."
                )
            else:
                reward += 0.1
                self._safe_set_message("Case marked within tolerance.")

        elif action == "request_reason":
            if workflow["deviation_flagged"]:
                if not workflow["reason_requested"]:
                    workflow["reason_requested"] = True
                    reward += 0.15
                    self._safe_set_message("Reason requested from site operator.")
                else:
                    self._safe_set_message("Reason had already been requested.")
            else:
                reward -= 0.15
                self._safe_set_message("Deviation must be flagged before requesting reason.")

        elif action.startswith("record_reason:"):
            reason = self._extract_value(action, "record_reason:")
            if workflow["reason_requested"] and workflow["deviation_flagged"]:
                if not workflow["reason_recorded"]:
                    workflow["reason_recorded"] = True
                    self.state["reason_code"] = reason
                    self.state["grader"]["documentation_complete"] = True
                    reward += 0.1
                    self._safe_set_message(f"Reason recorded: {reason}.")
                else:
                    self._safe_set_message("Reason already recorded.")
            else:
                reward -= 0.15
                self._safe_set_message("Request reason before recording it.")

        elif action == "place_hold":
            if workflow["deviation_flagged"]:
                if not workflow["processing_hold"]:
                    workflow["processing_hold"] = True
                    facts["processing_status"] = "on_hold"
                    self.state["grader"]["workflow_safeguarded"] = True
                    reward += 0.2
                    self._safe_set_message("Processing hold placed successfully.")
                else:
                    self._safe_set_message("Processing is already on hold.")
            else:
                reward -= 0.2
                self._safe_set_message("Flag deviation before placing a hold.")

        elif action == "release_hold":
            if workflow["processing_hold"] and workflow["reason_recorded"]:
                workflow["processing_hold"] = False
                facts["processing_status"] = "released"
                reward += 0.05
                self._safe_set_message("Hold released after documentation.")
            else:
                self.state["grader"]["unsafe_action_taken"] = True
                reward -= 0.25
                self._safe_set_message("Hold cannot be released before required documentation.")

        elif action == "close_case":
            if (
                workflow["deviation_flagged"]
                and workflow["reason_requested"]
                and workflow["reason_recorded"]
                and self.state["grader"]["workflow_safeguarded"]
            ):
                workflow["case_closed"] = True
                self.state["done"] = True
                self.state["status"] = "resolved_correctly"
                self.state["grader"]["correct_disposition"] = True
                reward += 0.15
                self._safe_set_message("Case closed correctly.")
            else:
                workflow["case_closed"] = True
                self.state["done"] = True
                self.state["status"] = "closed_incorrectly"
                self.state["grader"]["unsafe_action_taken"] = True
                reward -= 0.25
                self._safe_set_message(
                    "Case closed prematurely without completing required controls."
                )

        else:
            reward -= 0.5
            self.state["last_action_error"] = "Unhandled action."
            self.state["last_action_message"] = "Unhandled action."

        return reward

    # -----------------------------
    # Task 2: Sample Mismatch
    # -----------------------------

    def _step_sample_mismatch(self, action):
        reward = 0.0
        facts = self.state["facts"]
        workflow = self.state["workflow"]
        is_mismatch = facts["scanned_child_sample_id"] not in facts["expected_child_sample_ids"]

        if action == "inspect_case":
            self.state["discovered_fields"]["case_details"] = True
            reward += 0.1
            self._safe_set_message(
                "Case inspected. Parent-child scan details are now visible."
            )

        elif action == "review_protocol":
            self.state["discovered_fields"]["protocol"] = True
            reward += 0.1
            self._safe_set_message(
                "Protocol reviewed. Traceability rule is now visible."
            )

        elif action == "flag_deviation":
            if is_mismatch:
                if not workflow["mismatch_flagged"]:
                    workflow["mismatch_flagged"] = True
                    self.state["grader"]["issue_identified"] = True
                    reward += 0.2
                    self._safe_set_message("Traceability mismatch flagged correctly.")
                else:
                    self._safe_set_message("Mismatch already flagged.")
            else:
                reward -= 0.2
                self._safe_set_message("No mismatch present in this case.")

        elif action == "block_separation":
            if workflow["mismatch_flagged"]:
                if not workflow["separation_blocked"]:
                    workflow["separation_blocked"] = True
                    facts["traceability_status"] = "blocked"
                    self.state["grader"]["workflow_safeguarded"] = True
                    reward += 0.2
                    self._safe_set_message("Separation blocked to protect traceability.")
                else:
                    self._safe_set_message("Separation already blocked.")
            else:
                reward -= 0.2
                self._safe_set_message("Flag the mismatch before blocking separation.")

        elif action == "request_rescan":
            if workflow["separation_blocked"]:
                if not workflow["correct_child_requested"]:
                    workflow["correct_child_requested"] = True
                    reward += 0.15
                    self._safe_set_message(
                        "Operator instructed to rescan the correct child tube."
                    )
                else:
                    self._safe_set_message("Rescan had already been requested.")
            else:
                reward -= 0.15
                self._safe_set_message("Block separation before requesting rescan.")

        elif action.startswith("record_disposition:"):
            disposition = self._extract_value(action, "record_disposition:")
            if disposition == "traceability_restored" and workflow["correct_child_requested"]:
                workflow["traceability_restored"] = True
                facts["traceability_status"] = "restored"
                self.state["grader"]["documentation_complete"] = True
                reward += 0.15
                self._safe_set_message("Traceability restoration recorded.")
            else:
                reward -= 0.15
                self._safe_set_message("Valid restoration can only be recorded after rescan workflow.")

        elif action == "close_case":
            if (
                workflow["mismatch_flagged"]
                and workflow["separation_blocked"]
                and workflow["correct_child_requested"]
                and workflow["traceability_restored"]
            ):
                workflow["case_closed"] = True
                self.state["done"] = True
                self.state["status"] = "resolved_correctly"
                self.state["grader"]["correct_disposition"] = True
                reward += 0.15
                self._safe_set_message("Mismatch case closed correctly.")
            else:
                workflow["case_closed"] = True
                self.state["done"] = True
                self.state["status"] = "closed_incorrectly"
                self.state["grader"]["unsafe_action_taken"] = True
                reward -= 0.25
                self._safe_set_message(
                    "Mismatch case closed before restoring traceability."
                )

        else:
            reward -= 0.5
            self.state["last_action_error"] = "Unhandled action."
            self.state["last_action_message"] = "Unhandled action."

        return reward

    # -----------------------------
    # Task 3: Hemolyzed Sample
    # -----------------------------

    def _step_hemolyzed_sample(self, action):
        reward = 0.0
        facts = self.state["facts"]
        workflow = self.state["workflow"]
        is_hemolyzed = facts["sample_condition"] == "hemolyzed"

        if action == "inspect_case":
            self.state["discovered_fields"]["case_details"] = True
            reward += 0.1
            self._safe_set_message(
                "Case inspected. Sample quality and storage state are now visible."
            )

        elif action == "review_protocol":
            self.state["discovered_fields"]["protocol"] = True
            reward += 0.1
            self._safe_set_message(
                "Protocol reviewed. Supervisor review requirement is now visible."
            )

        elif action == "flag_deviation":
            if is_hemolyzed:
                if not workflow["quality_issue_flagged"]:
                    workflow["quality_issue_flagged"] = True
                    self.state["grader"]["issue_identified"] = True
                    reward += 0.2
                    self._safe_set_message("Quality issue flagged correctly.")
                else:
                    self._safe_set_message("Quality issue already flagged.")
            else:
                reward -= 0.2
                self._safe_set_message("No quality issue is present in this case.")

        elif action == "place_hold":
            if workflow["quality_issue_flagged"]:
                if not workflow["storage_hold"]:
                    workflow["storage_hold"] = True
                    facts["storage_status"] = "on_hold"
                    self.state["grader"]["workflow_safeguarded"] = True
                    reward += 0.2
                    self._safe_set_message("Storage hold applied.")
                else:
                    self._safe_set_message("Storage already on hold.")
            else:
                reward -= 0.2
                self._safe_set_message("Flag the issue before placing a hold.")

        elif action == "request_supervisor_review":
            if workflow["storage_hold"]:
                if not workflow["supervisor_review_requested"]:
                    workflow["supervisor_review_requested"] = True
                    facts["supervisor_review_status"] = "requested"
                    reward += 0.15
                    self._safe_set_message("Supervisor review requested.")
                else:
                    self._safe_set_message("Supervisor review already requested.")
            else:
                reward -= 0.15
                self._safe_set_message("Place the storage hold before requesting review.")

        elif action.startswith("record_disposition:"):
            disposition = self._extract_value(action, "record_disposition:")
            if workflow["supervisor_review_requested"]:
                if disposition == "reject_sample":
                    workflow["disposition_recorded"] = True
                    workflow["replacement_required"] = True
                    self.state["disposition"] = disposition
                    facts["supervisor_review_status"] = "completed"
                    self.state["grader"]["documentation_complete"] = True
                    reward += 0.15
                    self._safe_set_message(
                        "Disposition recorded: reject sample and request replacement."
                    )
                elif disposition == "store_with_approval":
                    workflow["disposition_recorded"] = True
                    workflow["replacement_required"] = False
                    self.state["disposition"] = disposition
                    facts["supervisor_review_status"] = "completed"
                    self.state["grader"]["documentation_complete"] = True
                    reward += 0.1
                    self._safe_set_message(
                        "Disposition recorded: storage allowed with supervisor approval."
                    )
                else:
                    reward -= 0.15
                    self._safe_set_message("Unsupported disposition value.")
            else:
                reward -= 0.15
                self._safe_set_message("Request supervisor review before recording disposition.")

        elif action == "escalate_case":
            if workflow["quality_issue_flagged"] and workflow["storage_hold"]:
                reward += 0.05
                self._safe_set_message("Case escalated for additional oversight.")
            else:
                reward -= 0.1
                self._safe_set_message("Escalation is premature without a confirmed held issue.")

        elif action == "close_case":
            if (
                workflow["quality_issue_flagged"]
                and workflow["storage_hold"]
                and workflow["supervisor_review_requested"]
                and workflow["disposition_recorded"]
            ):
                workflow["case_closed"] = True
                self.state["done"] = True
                self.state["status"] = "resolved_correctly"
                self.state["grader"]["correct_disposition"] = True
                reward += 0.15
                self._safe_set_message("Hemolyzed sample case closed correctly.")
            else:
                workflow["case_closed"] = True
                self.state["done"] = True
                self.state["status"] = "closed_incorrectly"
                self.state["grader"]["unsafe_action_taken"] = True
                reward -= 0.25
                self._safe_set_message(
                    "Case closed before review and disposition were completed."
                )

        else:
            reward -= 0.5
            self.state["last_action_error"] = "Unhandled action."
            self.state["last_action_message"] = "Unhandled action."

        return reward