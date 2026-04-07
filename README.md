# Clinical Deviation Environment

A lightweight OpenEnv-style environment for handling structured clinical workflow deviations in sample collection and processing.

---

## Tasks

This environment supports 3 tasks:

### 1. Timing Deviation in Blood Collection
- Sample collected outside protocol tolerance
- Agent must flag deviation, request reason, hold processing, and close correctly

### 2. Sample Mismatch During Separation
- Scanned child sample does not belong to selected parent sample
- Agent must flag mismatch, block separation, request correct child sample, and close correctly

### 3. Hemolyzed Sample Before Storage
- Sample marked hemolyzed after separation, with supervisor review still pending
- Agent must flag quality issue, hold storage, request supervisor review, and close correctly

---

## API Endpoints

- `GET /`  
  Health check endpoint

- `GET /tasks`  
  Returns all available tasks with descriptions and allowed actions

- `POST /reset`  
  Starts a new episode  
  Request body (optional):
  ```json
  { "case_type": "timing_deviation" }

- `GET /grader`
   Returns final score (0.0–1.0) for the current episode
   
- `GET /state`
   Returns current environment state

- `POST /step`  
  Takes an action and advances the environment  

  Request body:
  ```json
  { "action": "inspect_case" }

## Run locally

```bash
uvicorn app.server:app --reload
```

## Run inference

From the project root:

```bash
python inference.py
```