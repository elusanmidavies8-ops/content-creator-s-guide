"""Settings tests. Env-driven, no .env required."""

import pytest
from pydantic import SecretStr, ValidationError

from postwise.config import Settings, get_settings


def test_defaults_are_safe_for_dev():
    s = Settings(_env_file=None)
    assert s.app_env == "dev"
    assert s.llm_provider == "fake"  # tests never hit network by default


def test_unknown_provider_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_provider="anthropic")  # type: ignore[arg-type]


def test_empty_api_key_becomes_none():
    s = Settings(_env_file=None, llm_api_key="")
    assert s.llm_api_key is None


def test_api_key_is_secret():
    s = Settings(_env_file=None, llm_api_key="sk-xyz")
    assert isinstance(s.llm_api_key, SecretStr)
    assert "sk-xyz" not in repr(s.llm_api_key)


def test_timeout_bounds():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_timeout_s=0)


def test_get_settings_is_cached():
    get_settings.cache_clear()
    a = get_settings()
    b = get_settings()
    assert a is b
    get_settings.cache_clear()
