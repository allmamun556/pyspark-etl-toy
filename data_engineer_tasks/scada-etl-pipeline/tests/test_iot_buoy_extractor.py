from datetime import datetime, timezone

from src.extract.iot_buoy_extractor import parse_realtime2
from src.validation.external_validators import validate_buoy_reading

# Fixed fixture shaped exactly like NOAA NDBC's realtime2 text feed, so
# these tests never touch the network. Newest reading is the first data
# row; "MM" marks a missing sensor value.
SAMPLE_TEXT = """\
#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE
#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   hPa  degC  degC  degC  nmi  hPa    ft
2026 07 31 11 40  10  4.0  4.0   1.2    MM   6.6 191 1021.2    MM  16.8    MM   MM   MM    MM
2026 07 31 11 30 360  4.0  6.0    MM    MM    MM  MM 1021.0    MM    MM    MM   MM   MM    MM
"""


def test_parse_realtime2_takes_newest_row():
    reading = parse_realtime2(SAMPLE_TEXT, station_id="46050")
    assert reading.station_id == "46050"
    assert reading.ts == datetime(2026, 7, 31, 11, 40, tzinfo=timezone.utc)
    assert reading.wind_speed_ms == 4.0
    assert reading.wind_gust_ms == 4.0
    assert reading.wave_height_m == 1.2
    assert reading.pressure_hpa == 1021.2
    assert reading.water_temp_c == 16.8


def test_parse_realtime2_missing_value_becomes_none():
    reading = parse_realtime2(SAMPLE_TEXT, station_id="46050")
    assert reading.air_temp_c is None


def test_valid_buoy_reading_passes():
    reading = parse_realtime2(SAMPLE_TEXT, station_id="46050")
    result = validate_buoy_reading(reading)
    assert result.is_valid
    assert result.reasons == []


def test_buoy_reading_missing_wind_speed_fails():
    reading = parse_realtime2(SAMPLE_TEXT, station_id="46050")
    reading.wind_speed_ms = None
    result = validate_buoy_reading(reading)
    assert not result.is_valid
    assert any("wind_speed_ms" in r for r in result.reasons)


def test_buoy_reading_out_of_range_wave_height_fails():
    reading = parse_realtime2(SAMPLE_TEXT, station_id="46050")
    reading.wave_height_m = 99.0
    result = validate_buoy_reading(reading)
    assert not result.is_valid
    assert any("wave_height_m" in r for r in result.reasons)
