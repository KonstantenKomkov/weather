from datetime import date
from os import path
from unittest.mock import MagicMock

import pytest

from main.management.weather_parser import processing, queries
from main.models import Cloudiness, Country, Place, WeatherStation, WeatherStationType


def _rp5_data_row(fields: list[str]) -> str:
    """Строка в формате rp5.ru: split('\";\"'), дата в кавычках с удвоенной closing quote."""
    inner = '";"'.join(fields[1:])
    return f'"{fields[0]}"";"' + inner


def _synop_data_row(overrides: dict[int, str] | None = None) -> str:
    fields = ["null"] * 28
    defaults = {
        0: "01.01.2024 12:00",
        1: "5.0",
        2: "750.0",
        6: "ветер, дующий с юга",
        10: "Облаков нет.",
        14: "-5.0",
        15: "10.0",
        17: "Облаков нет.",
        21: "10.0",
    }
    for index, value in defaults.items():
        fields[index] = value
    if overrides:
        for index, value in overrides.items():
            fields[index] = value
    return _rp5_data_row(fields)


def _metar_data_row(overrides: dict[int, str] | None = None) -> str:
    fields = ["null"] * 13
    defaults = {
        0: "01.01.2024 12:00",
        1: "3.0",
        2: "760.0",
        5: "ветер, дующий с запада",
        10: "Облаков нет.",
        11: "10.0 и более",
    }
    for index, value in defaults.items():
        fields[index] = value
    if overrides:
        for index, value in overrides.items():
            fields[index] = value
    return _rp5_data_row(fields)


def _synop_lines(data_row: str) -> list[str]:
    return [f"header{i}" for i in range(7)] + [data_row]


def _metar_lines(data_row: str) -> list[str]:
    return [f"header{i}" for i in range(7)] + [data_row]


def _make_station(**kwargs) -> WeatherStation:
    country = Country(name=kwargs.get("country_name", "Россия"))
    place = Place(
        name=kwargs.get("place_name", "Москва"),
        country=country,
        latitude=kwargs.get("latitude", 55.75),
        longitude=kwargs.get("longitude", 37.62),
    )
    station_type = WeatherStationType(type=kwargs.get("station_type", "метеостанция"))
    return WeatherStation(
        number=kwargs.get("number", "27612"),
        rp5_link=kwargs.get("rp5_link", "https://rp5.ru/27612"),
        place=place,
        type=station_type,
        last_date=kwargs.get("last_date", date(2024, 1, 1)),
        metar=kwargs.get("metar"),
    )


def test_insert_csv_weather_station_query():
    sql = queries.insert_csv_weather_station_data("/tmp/data.csv", "#")
    assert "COPY weather" in sql
    assert "/tmp/data.csv" in sql
    assert "DELIMITER '#'" in sql


def test_insert_csv_metar_query():
    sql = queries.insert_csv_metar_data("/tmp/metar.csv", "#")
    assert "COPY weather" in sql
    assert "/tmp/metar.csv" in sql
    assert 'visibility, dew_point' in sql


def test_weather_stations_data_processing_maps_fields():
    lines = _synop_lines(_synop_data_row())
    result = processing.weather_stations_data_processing("#", lines, 42).decode("utf-8")

    assert result.startswith("weather_station_id#")
    data_line = result.splitlines()[1]
    parts = data_line.split("#")
    assert parts[0] == "42"
    assert parts[1] == "2024-01-01 12:00:00"
    assert parts[2] == "5.0"
    assert parts[3] == "750.0"
    assert parts[7] == "1"
    assert parts[11] == "1"
    assert parts[18] == "1"


def test_weather_stations_data_processing_rejects_out_of_range_values():
    row = _synop_data_row({1: "150.0", 2: "400.0"})
    result = processing.weather_stations_data_processing("#", _synop_lines(row), 1).decode("utf-8")
    parts = result.splitlines()[1].split("#")

    assert parts[2] == "null"
    assert parts[3] == "null"


def test_weather_stations_data_processing_unknown_wind_becomes_null():
    row = _synop_data_row({6: "неизвестный ветер"})
    result = processing.weather_stations_data_processing("#", _synop_lines(row), 1).decode("utf-8")
    parts = result.splitlines()[1].split("#")

    assert parts[7] == "null"


@pytest.mark.django_db
def test_get_cloudiness_id_returns_existing(reset_cloudiness_cache):
    existing = Cloudiness.objects.create(description="рассеянная", scale=3)

    assert processing.get_cloudiness_id("рассеянная") == existing.pk
    assert Cloudiness.objects.count() == 1


@pytest.mark.django_db
def test_get_cloudiness_id_creates_new(reset_cloudiness_cache):
    cloudiness_id = processing.get_cloudiness_id("новая облачность")

    assert Cloudiness.objects.filter(pk=cloudiness_id, description="новая облачность").exists()


@pytest.mark.django_db
def test_metar_data_processing_resolves_cloudiness(reset_cloudiness_cache):
    cloudiness = Cloudiness.objects.create(description="Облаков нет.", scale=0)
    lines = _metar_lines(_metar_data_row())
    result = processing.metar_data_processing("#", lines, 7).decode("utf-8")
    parts = result.splitlines()[1].split("#")

    assert parts[0] == "7"
    assert parts[11] == str(cloudiness.pk)
    assert parts[12] == "10.0"


@pytest.mark.django_db
def test_find_or_write_country_creates_and_reuses():
    from main.management.weather_parser import parser_main

    station = _make_station(country_name="Беларусь")

    countries, country = parser_main.find_or_write_country([], station)
    assert country.pk is not None
    assert country.name == "Беларусь"
    assert Country.objects.filter(name="Беларусь").exists()

    countries, same_country = parser_main.find_or_write_country(countries, station)
    assert same_country.pk == country.pk
    assert Country.objects.filter(name="Беларусь").count() == 1


@pytest.mark.django_db
def test_find_or_write_weather_station_type_creates_and_reuses():
    from main.management.weather_parser import parser_main

    station = _make_station(station_type="METAR")

    types, station_type = parser_main.find_or_write_weather_station_type([], station)
    assert station_type.pk is not None
    assert station_type.type == "METAR"

    types, same_type = parser_main.find_or_write_weather_station_type(types, station)
    assert same_type.pk == station_type.pk
    assert WeatherStationType.objects.filter(type="METAR").count() == 1


@pytest.mark.django_db
def test_find_or_write_place_creates_and_reuses():
    from main.management.weather_parser import parser_main

    station = _make_station(place_name="Санкт-Петербург", latitude=59.93, longitude=30.31)
    country = Country.objects.create(name="Россия")

    places, place = parser_main.find_or_write_place([], station, country)
    assert place.pk is not None
    assert place.name == "Санкт-Петербург"
    assert place.country_id == country.pk

    places, same_place = parser_main.find_or_write_place(places, station, country)
    assert same_place.pk == place.pk
    assert Place.objects.filter(name="Санкт-Петербург").count() == 1


@pytest.mark.django_db
def test_find_or_write_weather_station_creates_and_reuses():
    from main.management.weather_parser import parser_main

    country = Country.objects.create(name="Россия")
    place = Place.objects.create(name="Казань", country=country, latitude=55.79, longitude=49.12)
    station_type = WeatherStationType.objects.create(type="метеостанция")
    station = _make_station(number="12345", rp5_link="https://rp5.ru/12345", place_name="Казань")

    weather_stations, saved_station = parser_main.find_or_write_weather_station(
        [], station, place, station_type,
    )
    assert saved_station.pk is not None
    assert saved_station.number == "12345"

    weather_stations, same_station = parser_main.find_or_write_weather_station(
        weather_stations, station, place, station_type,
    )
    assert same_station.pk == saved_station.pk
    assert WeatherStation.objects.filter(number="12345").count() == 1


@pytest.mark.django_db
def test_get_cloudiness_id_refreshes_after_cache_reset(reset_cloudiness_cache):
    processing.get_cloudiness_id("первая")
    second = Cloudiness.objects.create(description="вторая", scale=1)

    processing.reset_cloudiness_cache()

    assert processing.get_cloudiness_id("вторая") == second.pk


def _setup_load_csv_fixture(tmp_path, monkeypatch, *, delete_csv_files: bool):
    from main.management.weather_parser import parser_main
    from django.db import connection

    folder = "27612"
    csv_dir = tmp_path / folder
    csv_dir.mkdir()
    csv_file = csv_dir / "2024.csv"
    csv_file.write_text("header\n", encoding="utf-8")

    static_root = str(tmp_path) + path.sep
    monkeypatch.setattr(parser_main, "_STATIC_ROOT", static_root)
    monkeypatch.setitem(parser_main.WEATHER_PARSER, "DELETE_CSV_FILES", delete_csv_files)

    executed: list[str] = []
    cursor = MagicMock()
    cursor.execute.side_effect = lambda sql: executed.append(sql)
    cursor_context = MagicMock()
    cursor_context.__enter__.return_value = cursor
    cursor_context.__exit__.return_value = False
    monkeypatch.setattr(connection, "cursor", lambda: cursor_context)

    station_type = WeatherStationType(type="метеостанция")
    return parser_main, folder, csv_file, executed, station_type


@pytest.mark.django_db
def test_load_data_from_csv_executes_copy(tmp_path, monkeypatch):
    parser_main, folder, csv_file, executed, station_type = _setup_load_csv_fixture(
        tmp_path, monkeypatch, delete_csv_files=True,
    )

    assert parser_main.load_data_from_csv(folder, station_type) is True
    copy_sql = [sql for sql in executed if sql.startswith("COPY weather")]
    assert len(copy_sql) == 1
    assert str(csv_file) in copy_sql[0]
    assert csv_file.exists()


@pytest.mark.django_db
def test_load_data_from_csv_removes_file_on_success(tmp_path, monkeypatch):
    parser_main, folder, csv_file, _executed, station_type = _setup_load_csv_fixture(
        tmp_path, monkeypatch, delete_csv_files=False,
    )

    assert parser_main.load_data_from_csv(folder, station_type) is True
    assert not csv_file.exists()


@pytest.mark.django_db
def test_load_data_from_csv_keeps_file_on_other_db_error(tmp_path, monkeypatch):
    from django.db import connection
    from django.db.utils import DatabaseError

    parser_main_mod, folder, csv_file, _executed, station_type = _setup_load_csv_fixture(
        tmp_path, monkeypatch, delete_csv_files=False,
    )

    cursor = MagicMock()
    cursor.execute.side_effect = DatabaseError("syntax error")
    cursor_context = MagicMock()
    cursor_context.__enter__.return_value = cursor
    cursor_context.__exit__.return_value = False
    monkeypatch.setattr(connection, "cursor", lambda: cursor_context)

    assert parser_main_mod.load_data_from_csv(folder, station_type) is False
    assert csv_file.exists()


@pytest.mark.django_db
def test_load_data_from_csv_removes_file_on_duplicate(tmp_path, monkeypatch):
    from django.db import connection
    from django.db.utils import IntegrityError

    parser_main_mod, folder, csv_file, _executed, station_type = _setup_load_csv_fixture(
        tmp_path, monkeypatch, delete_csv_files=False,
    )

    cursor = MagicMock()
    cursor.execute.side_effect = IntegrityError("duplicate key")
    cursor_context = MagicMock()
    cursor_context.__enter__.return_value = cursor
    cursor_context.__exit__.return_value = False
    monkeypatch.setattr(connection, "cursor", lambda: cursor_context)

    assert parser_main_mod.load_data_from_csv(folder, station_type) is False
    assert not csv_file.exists()
