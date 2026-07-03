from weather.config import Settings, get_settings


def test_settings_defaults():
    settings = Settings(_env_file=None)
    assert settings.debug is True
    assert settings.csv_delimiter == "#"
    assert settings.db_engine == "django.db.backends.postgresql"


def test_allowed_hosts_parsing():
    settings = Settings(_env_file=None, allowed_hosts="localhost, 127.0.0.1 ,web")
    assert settings.allowed_hosts_list == ["localhost", "127.0.0.1", "web"]


def test_database_configured_flag(monkeypatch):
    monkeypatch.setenv("DB_NAME", "")
    settings = Settings(_env_file=None)
    assert settings.database_configured is False

    monkeypatch.setenv("DB_NAME", "weather_db")
    settings = Settings(_env_file=None)
    assert settings.database_configured is True


def test_get_settings_cached():
    assert get_settings() is get_settings()
