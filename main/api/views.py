from rest_framework import viewsets
from .serializers import WeatherSerializer, WeatherStationSerializer, WeatherStationListRetrieveSerializer
from ..models import Weather, WeatherStation


class WeatherViewSet(viewsets.ModelViewSet):

    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer


class WeatherStationViewSet(viewsets.ModelViewSet):

    queryset = WeatherStation.objects.all()
    serializer_class = WeatherStationSerializer

    action_to_serializer = {
        "list": WeatherStationListRetrieveSerializer,
        "retrieve": WeatherStationListRetrieveSerializer,
    }

    def get_serializer_class(self):
        return self.action_to_serializer.get(
            self.action,
            self.serializer_class
        )