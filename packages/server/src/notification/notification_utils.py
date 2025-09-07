from firebase_admin import messaging

from src.model.app.task import Task, TaskStatus


def send_push_notification(task: Task, status: TaskStatus):
    if status == TaskStatus.FAILED:
        title = "Task failed"
        body = f"{task.title} couldn't be completed. Tap to see details and try again."
    else:
        title = "Task complete"
        body = f"{task.title} finished. Tap to review the changes."

    notification = messaging.Notification(
        title=title,
        body=body,
    )
    message = messaging.Message(
        data={
            "taskId": task.id,
        },
        notification=notification,
        topic=task.id,
    )
    messaging.send(message)
