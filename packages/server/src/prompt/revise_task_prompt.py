REVISE_TASK_PROMPT = """
You are working on revising the implementation for the task: {task_title}

## Task Requirements
{task_requirements}

## User Feedback to Address
{feedback_task_description}

Please address all the user feedback by making the necessary code changes. Focus on:
1. Carefully reading and understanding each feedback comment
2. Making precise changes to address the specific concerns raised
3. Ensuring your changes maintain code quality and don't break existing functionality
4. Following the existing code style and patterns in the repository

Make all necessary changes to address the feedback and ensure the implementation meets the user's expectations.
"""
