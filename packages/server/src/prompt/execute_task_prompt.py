EXECUTE_TASK_PROMPT = """
Your goal is to implement the given coding task.

## Task Context
This coding subtask is part of a larger task: "{task_title}"

**Task Description**
{task_body}

**Task Requirements**
{task_requirements}

## Subtask Position
This is subtask {subtask_number} in the task.

## Previously Implemented Subtasks
The following subtasks have already been implemented in this task. You can examine the changes using git show:
{completed_subtask_commits}

## Current Subtask
**Subtask Title** {subtask_title}

**Subtask Description**
{subtask_description}

Please implement this subtask following best practices and ensuring it integrates well with the existing codebase and previously completed subtasks.
Please ensure linting, build, and unit tests all pass, and fix any failures caused by your changes.
Please do not write more than required.
"""

EXECUTE_TASK_SYSTEM_PROMPT = """
## Important Rules
- Always implement the requested changes to the codebase. Do not just suggest or describe changes - actually modify the files.
- KEEP IMPLEMENTATIONS CONCISE. ONLY IMPLEMENT WHAT THE SUBTASK SPECIFIES.
- NEVER modify dependencies, e.g. package.json or package-lock.json files.
"""

REMOVE_COMMENTS_PROMPT = """
Run git diff to see what was just added to this file. 
Remove comments only from the lines that show as additions (+ prefix in git diff). Do not modify any existing lines or remove any original comments.
"""
