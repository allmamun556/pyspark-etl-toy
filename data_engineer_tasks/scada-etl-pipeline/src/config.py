"""
Centralized, environment-driven configuration.

Best practice: never hardcode connection strings, thresholds, or credentials
in pipeline code. Everything here is overridable via environment variables
(or a .env file locally), which keeps dev/staging/prod configuration
identical in code and different only in environment.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Database ---
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "scada"
    postgres_user: str = "scada_user"
    postgres_password: str = "change_me_in_prod"

    # --- Pipeline behavior ---
    turbine_count: int = 20
    reading_interval_seconds: int = 600
    load_batch_size: int = 5000

    # --- Physical validation bounds (wind turbine SCADA) ---
    max_wind_speed_ms: float = 45.0
    max_power_kw: float = 3500.0
    max_rotor_rpm: float = 20.0
    min_nacelle_temp_c: float = -30.0
    max_nacelle_temp_c: float = 60.0

    # --- Solar plant simulation + validation bounds ---
    solar_plant_count: int = 8
    solar_capacity_kwp: float = 5000.0
    solar_inverter_ac_capacity_kw: float = 4500.0
    max_irradiance_w_m2: float = 1400.0
    min_panel_temp_c: float = -20.0
    max_panel_temp_c: float = 90.0
    # A little headroom above nameplate capacity - inverters can briefly
    # exceed rated output under cool, high-irradiance conditions.
    max_dc_power_kw: float = 5500.0
    max_ac_power_kw: float = 5000.0

    # How old the most recent weather_api_readings row may be before the
    # solar simulator stops trusting it as an irradiance anchor and falls
    # back to its own clear-sky model unanchored.
    reference_irradiance_max_staleness_minutes: int = 180

    # --- Data quality: timeliness ---
    # How far into the future a reading's timestamp may be before it's
    # rejected as bad data rather than accepted as normal clock skew.
    max_future_skew_seconds: int = 300

    # --- External data sources (real, live, no API key required) ---
    # HTTP API: Open-Meteo (https://open-meteo.com) - ambient weather for a
    # real North Sea wind-energy hub (Bremerhaven, Germany).
    weather_api_base_url: str = "https://api.open-meteo.com/v1/forecast"
    weather_latitude: float = 53.55
    weather_longitude: float = 8.09

    # IoT: NOAA National Data Buoy Center - real moored ocean buoys
    # transmitting live sensor telemetry. Station 46050 (Stonewall Bank, OR)
    # is an active station in a US offshore-wind-relevant corridor.
    iot_buoy_base_url: str = "https://www.ndbc.noaa.gov/data/realtime2"
    iot_buoy_station_id: str = "46050"

    http_request_timeout_seconds: int = 10

    # How old the most recent weather_api_readings row may be before the
    # SCADA simulator stops trusting it as a wind-speed anchor and falls
    # back to its unanchored random default.
    reference_wind_max_staleness_minutes: int = 180

    # --- Logging ---
    log_level: str = "INFO"

    # --- Alerting ---
    # Slack incoming-webhook URL for DAG failure notifications. Unset by
    # default - src/utils/alerting.py no-ops (logs instead of raising) when
    # this is empty, so the pipeline never fails *because* alerting isn't
    # configured. Create one at https://api.slack.com/messaging/webhooks.
    slack_webhook_url: str | None = None

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Settings are cached so we parse the environment once per process."""
    return Settings()
