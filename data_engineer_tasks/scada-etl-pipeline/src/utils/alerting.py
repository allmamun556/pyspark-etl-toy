"""
DAG failure alerting via a Slack incoming webhook.

Deliberately a soft dependency: if SLACK_WEBHOOK_URL isn't set, or the POST
itself fails, this logs and returns rather than raising - alerting
infrastructure must never become a new way for a DAG run to fail.
Structured logs and the audit tables are necessary but not sufficient for
real observability; someone has to actually be notified when a run fails,
not just have it be visible if they go looking.
"""
from __future__ import annotations

import requests

from src.config import get_settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def notify_dag_failure(context: dict) -> None:
    """
    Airflow on_failure_callback signature: called with the task instance
    context. Wire into a DAG's default_args as on_failure_callback so every
    task in it is covered without repeating this per-task.
    """
    settings = get_settings()
    if not settings.slack_webhook_url:
        logger.info("slack_webhook_url not configured - skipping failure notification")
        return

    task_instance = context.get("task_instance")
    dag_id = context.get("dag").dag_id if context.get("dag") else "unknown_dag"
    task_id = task_instance.task_id if task_instance else "unknown_task"
    run_id = context.get("run_id", "unknown_run")
    exception = context.get("exception")
    log_url = getattr(task_instance, "log_url", None) if task_instance else None

    text = (
        f":rotating_light: *Airflow task failed*\n"
        f"*DAG:* `{dag_id}`   *Task:* `{task_id}`\n"
        f"*Run:* `{run_id}`\n"
        f"*Error:* {exception}\n"
    )
    if log_url:
        text += f"<{log_url}|View logs>"

    try:
        response = requests.post(
            settings.slack_webhook_url,
            json={"text": text},
            timeout=settings.http_request_timeout_seconds,
        )
        response.raise_for_status()
    except Exception:
        # A broken webhook must not mask the original task failure - log
        # and move on, don't re-raise.
        logger.exception("failed to send Slack failure notification for %s.%s", dag_id, task_id)
