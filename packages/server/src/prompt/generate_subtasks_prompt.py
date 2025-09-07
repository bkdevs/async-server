GENERATE_SUBTASKS_PROMPT = """
Generate an execution plan and output it to ASYNC_PLAN_BREAKDOWN.json with this precise format:
[
  {
    "title": "Clear subtask objective",
    "steps": [
      "actionable step 1",
      "actionable step 2",
      ...
    ]
  }
]

## Rules
- Each subtask should be self-contained and reviewable by itself
- Do as minimal as possible that meets the requirements, do not write more than necessary

Do NOT include the following types of tasks in your plan:
- QA or testing phases (unless explicitly part of the core development requirement)
- Rollout or deployment tasks  
- General "validation" or "verification" steps
- Manual testing instructions
- Code review processes

## Task Description
"""
