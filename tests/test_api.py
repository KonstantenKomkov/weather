import pytest


@pytest.mark.django_db
def test_weather_stations_list(client):
    response = client.get("/api/weather_stations/")
    assert response.status_code == 200
    assert "results" in response.json()


@pytest.mark.django_db
def test_weather_list(client):
    response = client.get("/api/weather/")
    assert response.status_code == 200
    assert "results" in response.json()


def test_schema_endpoint(client):
    response = client.get("/api/schema/")
    assert response.status_code == 200


def test_health_like_root(client):
    response = client.get("/api/docs/")
    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
