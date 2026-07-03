import pytest

import main.management.weather_parser.processing as processing_module


@pytest.fixture
def reset_cloudiness_cache():
    processing_module.reset_cloudiness_cache()
    yield
    processing_module.reset_cloudiness_cache()
