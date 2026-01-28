import pytest_check as check

from app.config import settings


def test_settings_loaded():
    """Verify that settings from environment loaded, they are.

    API key present must be, model configured it should be.
    """
    check.is_not_none(settings.llm_api_key, "LLM API key missing, it is!")
    check.is_not_none(settings.llm_model, "LLM model not configured, it is!")
    check.greater(settings.max_upload_size_mb, 0,
                  "Upload size invalid, it is!")


def test_settings_defaults():
    """Default values correct, verify we must.

    Sensible defaults, the Force requires.
    """
    check.equal(settings.log_level, "INFO", "Log level unexpected, it is!")
    check.is_in(settings.max_upload_size_mb, range(
        1, 101), "Upload size unreasonable, it is!")
