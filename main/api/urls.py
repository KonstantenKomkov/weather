from django.urls import path
from rest_framework import routers
from .views import WeatherViewSet, WeatherStationViewSet


router = routers.SimpleRouter()
router.register('weather', WeatherViewSet, basename='weather')
router.register('weather_stations', WeatherStationViewSet, basename='weather_stations')

urlpatterns = []
urlpatterns += router.urls