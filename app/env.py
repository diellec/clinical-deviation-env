class ClinicalEnv:
    def __init__(self):
        self.state = None

    def get_state(self):
        if self.state is None:
            return {"error": "No active episode. Call reset first."}
        return self.state

    def reset(self, case_type="timing_deviation"):
        if case_type == "timing_deviation":
            self.state = self._timing_deviation_case()
        elif case_type == "sample_mismatch":
            self.state = self._sample_mismatch_case()
        elif case_type == "hemolyzed_sample":
            self.state = self._hemolyzed_sample_case()
        else:
            raise ValueError(f"Unknown case_type: {case_type}")

        return self.state

    def _timing_deviation_case(self):
        return {
            "case_id": "timing_deviation_001",
            "case_type": "timing_deviation",
            "subject_id": "S-012",
            "activity": "Blood Collection",
            "scheduled_time": "10:00",
            "actual_time": "10:04",
            "tolerance_minutes": 2,
            "deviation_flagged": False,
            "processing_allowed": False,
            "processing_on_hold": False,
            "reason_requested": False,
            "steps_taken": [],
            "status": "in_progress",
            "available_actions": [
                "inspect_case",
                "flag_deviation",
                "request_reason",
                "hold_processing",
                "allow_processing",
                "close_case"
            ]
        }

    def _sample_mismatch_case(self):
        return {
            "case_id": "sample_mismatch_001",
            "case_type": "sample_mismatch",
            "activity": "Sample Separation",
            "parent_sample_id": "P-1001",
            "expected_child_sample_ids": ["C-2001", "C-2002"],
            "scanned_child_sample_id": "C-9999",
            "mismatch_flagged": False,
            "separation_blocked": False,
            "correct_child_requested": False,
            "steps_taken": [],
            "status": "in_progress",
            "available_actions": [
                "inspect_case",
                "flag_mismatch",
                "block_separation",
                "request_correct_child",
                "allow_separation",
                "close_case"
            ]
        }

    def _hemolyzed_sample_case(self):
        return {
            "case_id": "hemolyzed_sample_001",
            "case_type": "hemolyzed_sample",
            "activity": "Sample Storage",
            "parent_sample_id": "P-3001",
            "child_sample_id": "C-4001",
            "sample_condition": "hemolyzed",
            "current_stage": "post_separation",
            "supervisor_review_done": False,
            "quality_issue_flagged": False,
            "storage_on_hold": False,
            "review_requested": False,
            "steps_taken": [],
            "status": "in_progress",
            "available_actions": [
                "inspect_case",
                "flag_quality_issue",
                "hold_storage",
                "request_supervisor_review",
                "allow_storage",
                "close_case"
            ]
        }

    def step(self, action):
        if self.state is None:
            return {"error": "Call reset first"}

        self.state["steps_taken"].append(action)

        if self.state["case_type"] == "timing_deviation":
            return self._step_timing_deviation(action)
        elif self.state["case_type"] == "sample_mismatch":
            return self._step_sample_mismatch(action)
        elif self.state["case_type"] == "hemolyzed_sample":
            return self._step_hemolyzed_sample(action)
        else:
            return {"error": "Unknown case type"}

    def _step_timing_deviation(self, action):
        reward = 0
        done = False
        message = ""

        delay = 4
        tolerance = self.state["tolerance_minutes"]
        out_of_tolerance = delay > tolerance

        if action == "inspect_case":
            reward = 0.1
            message = "Case inspected. Sample exceeds tolerance."

        elif action == "flag_deviation":
            if out_of_tolerance:
                self.state["deviation_flagged"] = True
                reward = 0.3
                message = "Deviation flagged."
            else:
                reward = -0.2
                message = "Incorrect deviation flag."

        elif action == "request_reason":
            if self.state["deviation_flagged"]:
                self.state["reason_requested"] = True
                reward = 0.2
                message = "Reason requested."
            else:
                reward = -0.2
                message = "Must flag deviation first."

        elif action == "hold_processing":
            if self.state["deviation_flagged"]:
                self.state["processing_on_hold"] = True
                reward = 0.2
                message = "Processing on hold."
            else:
                reward = -0.3
                message = "Cannot hold without deviation."

        elif action == "allow_processing":
            if out_of_tolerance:
                reward = -0.5
                self.state["processing_allowed"] = True
                message = "Incorrectly allowed processing."
            else:
                reward = 0.2
                message = "Processing allowed."

        elif action == "close_case":
            if (
                self.state["deviation_flagged"]
                and self.state["reason_requested"]
                and self.state["processing_on_hold"]
            ):
                reward = 1.0
                done = True
                self.state["status"] = "resolved_correctly"
                message = "Case correctly resolved."
            else:
                reward = -0.5
                done = True
                self.state["status"] = "closed_incorrectly"
                message = "Case closed without proper steps."

        else:
            reward = -0.5
            message = "Invalid action."

        return {
            "state": self.state,
            "reward": reward,
            "done": done,
            "message": message
        }

    def _step_sample_mismatch(self, action):
        reward = 0
        done = False
        message = ""

        expected_children = self.state["expected_child_sample_ids"]
        scanned_child = self.state["scanned_child_sample_id"]
        is_mismatch = scanned_child not in expected_children

        if action == "inspect_case":
            reward = 0.1
            message = "Case inspected. Scanned child sample does not belong to parent."

        elif action == "flag_mismatch":
            if is_mismatch:
                self.state["mismatch_flagged"] = True
                reward = 0.3
                message = "Sample mismatch flagged."
            else:
                reward = -0.2
                message = "No mismatch present."

        elif action == "block_separation":
            if self.state["mismatch_flagged"]:
                self.state["separation_blocked"] = True
                reward = 0.3
                message = "Separation blocked."
            else:
                reward = -0.3
                message = "Must flag mismatch first."

        elif action == "request_correct_child":
            if self.state["separation_blocked"]:
                self.state["correct_child_requested"] = True
                reward = 0.2
                message = "Requested correct child sample."
            else:
                reward = -0.2
                message = "Block separation before requesting correction."

        elif action == "allow_separation":
            if is_mismatch:
                reward = -0.6
                message = "Incorrectly allowed separation with wrong child sample."
            else:
                reward = 0.2
                message = "Separation allowed."

        elif action == "close_case":
            if (
                self.state["mismatch_flagged"]
                and self.state["separation_blocked"]
                and self.state["correct_child_requested"]
            ):
                reward = 1.0
                done = True
                self.state["status"] = "resolved_correctly"
                message = "Mismatch case correctly resolved."
            else:
                reward = -0.5
                done = True
                self.state["status"] = "closed_incorrectly"
                message = "Mismatch case closed without proper steps."

        else:
            reward = -0.5
            message = "Invalid action."

        return {
            "state": self.state,
            "reward": reward,
            "done": done,
            "message": message
        }

    def _step_hemolyzed_sample(self, action):
        reward = 0
        done = False
        message = ""

        is_hemolyzed = self.state["sample_condition"] == "hemolyzed"

        if action == "inspect_case":
            reward = 0.1
            message = "Case inspected. Sample is marked hemolyzed and supervisor review is pending."

        elif action == "flag_quality_issue":
            if is_hemolyzed:
                self.state["quality_issue_flagged"] = True
                reward = 0.3
                message = "Quality issue flagged."
            else:
                reward = -0.2
                message = "No quality issue detected."

        elif action == "hold_storage":
            if self.state["quality_issue_flagged"]:
                self.state["storage_on_hold"] = True
                reward = 0.3
                message = "Storage placed on hold."
            else:
                reward = -0.3
                message = "Flag the quality issue before holding storage."

        elif action == "request_supervisor_review":
            if self.state["storage_on_hold"]:
                self.state["review_requested"] = True
                reward = 0.2
                message = "Supervisor review requested."
            else:
                reward = -0.2
                message = "Hold storage before requesting supervisor review."

        elif action == "allow_storage":
            if is_hemolyzed and not self.state["supervisor_review_done"]:
                reward = -0.6
                message = "Incorrectly allowed storage before supervisor review."
            else:
                reward = 0.2
                message = "Storage allowed."

        elif action == "close_case":
            if (
                self.state["quality_issue_flagged"]
                and self.state["storage_on_hold"]
                and self.state["review_requested"]
            ):
                reward = 1.0
                done = True
                self.state["status"] = "resolved_correctly"
                message = "Hemolyzed sample case correctly resolved."
            else:
                reward = -0.5
                done = True
                self.state["status"] = "closed_incorrectly"
                message = "Hemolyzed sample case closed without proper steps."

        else:
            reward = -0.5
            message = "Invalid action."

        return {
            "state": self.state,
            "reward": reward,
            "done": done,
            "message": message
        }