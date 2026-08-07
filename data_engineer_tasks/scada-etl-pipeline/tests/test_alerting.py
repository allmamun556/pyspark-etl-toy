from unittest.mock import MagicMock, patch

from src.config import get_settings
from src.utils.alerting import notify_dag_failure


def _context(**overrides):
    dag = MagicMock()
    dag.dag_id = "scada_etl_pipeline"
    task_instance = MagicMock()
    task_instance.task_id = "extract_transform_validate"
    task_instance.log_url = "http://airflow.local/log"
    context = {
        "dag": dag,
        "task_instance": task_instance,
        "run_id": "scheduled__2026-01-01T00:00:00+00:00",
        "exception": RuntimeError("boom"),
    }
    context.update(overrides)
    return context


def test_no_webhook_configured_skips_post(monkeypatch):
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    get_settings.cache_clear()

    with patch("src.utils.alerting.requests.post") as mock_post:
        notify_dag_failure(_context())
        mock_post.assert_not_called()

    get_settings.cache_clear()


def test_webhook_configured_posts_with_dag_and_task(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/T000/B000/XXXX")
    get_settings.cache_clear()

    with patch("src.utils.alerting.requests.post") as mock_post:
        mock_post.return_value = MagicMock(raise_for_status=MagicMock())
        notify_dag_failure(_context())

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://hooks.slack.com/services/T000/B000/XXXX"
        assert "scada_etl_pipeline" in kwargs["json"]["text"]
        assert "extract_transform_validate" in kwargs["json"]["text"]

    get_settings.cache_clear()


def test_post_failure_is_swallowed_not_raised(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/T000/B000/XXXX")
    get_settings.cache_clear()

    with patch("src.utils.alerting.requests.post", side_effect=ConnectionError("network down")):
        notify_dag_failure(_context())  # must not raise

    get_settings.cache_clear()
